# Especificação Técnica do Sistema (03-especs.md)

Este documento detalha a especificação técnica dos arquivos do Sistema de Encomenda de Produtos Artesanais Personalizados, mapeando ações, escopo e comportamento lógico.

---

## 1. Arquivos de Configuração e Ambiente

### `/requirements.txt`
- **ação:** criar
- **descrição:** Define as bibliotecas e dependências externas necessárias para a execução e persistência de dados do ecossistema Flask.
- **pseudocódigo:**
  ```text
  Flask==2.3.x
  Flask-SQLAlchemy==3.x
  Flask-Login==0.6.x
  Werkzeug==2.3.x
/.gitignore
ação: criar

descrição: Exclui diretórios locais de ambiente virtual, caches do Python e arquivos locais de banco de dados do controle de versão Git.

pseudocódigo:

Plaintext
venv/
__pycache__/
*.sqlite3
*.db
.env
/Dockerfile
ação: criar

descrição: Configura o roteiro automatizado para construção da imagem Docker isolada da aplicação.

pseudocódigo:

Dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
EXPOSE 5000
CMD ["python", "run.py"]
2. Inicialização do Sistema
/run.py
ação: criar

descrição: Script de ponto de entrada. Instancia o servidor web embutido apontando para a aplicação configurada.

pseudocódigo:

Python
importar 'app' do modulo 'app'
se __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
/app/__init__.py
ação: criar

descrição: Configura a Application Factory do Flask, lê as variáveis de ambiente essenciais, registra os Blueprints e injeta deterministicamente o Administrador padrão no banco de dados na primeira execução.

pseudocódigo:

Python
def create_app():
    instanciar Flask(app)
    app.config['SECRET_KEY'] = ler_variavel_ambiente('SECRET_KEY')
    app.config['SQLALCHEMY_DATABASE_URI'] = ler_variavel_ambiente('DATABASE_URL')

    inicializar db(app)
    inicializar login_manager(app)

    importar Blueprint 'main' de 'routes'
    registrar_blueprint(main)

    com app.app_context():
        db.create_all() # Garante a existência física das tabelas SQLite

        admin_user = ler_variavel_ambiente('ADMIN_USERNAME')
        admin_pass = ler_variavel_ambiente('ADMIN_PASSWORD')

        se nao existir Usuario com username == admin_user no banco:
            novo_admin = Usuario(username=admin_user, email='admin@example.com', password=gerar_hash(admin_pass), role='admin')
            db.session.add(novo_admin)
            db.session.commit()
        
        # Seeding: Pré-cadastro de 5 produtos iniciais
        se buscar_todos_os_produtos() estiver vazio:
            para i de 1 ate 5:
                criar_produto(nome=f"Produto {i}", descricao=f"Descrição {i}", imagem_url=f"/static/img/produto{i}.jpg")
    
    retornar app

3. Camada de Dados (Persistência)
/app/models.py
ação: criar

descrição: Mapeamento Objeto-Relacional (ORM) das entidades de Usuários e Pedidos estruturados conforme as regras de negócio.

pseudocódigo:

Python
classe User(db.Model, UserMixin):
    id = Inteiro, Chave Primaria
    username = String(80), Unico, Nao Nulo
    email = String(80), Unico, Nao Nulo
    password_hash = String(128), Nao Nulo
    role = String(20), Nao Nulo # Domínio fechado: 'admin', 'atendente', 'cliente'

classe Produto(db.Model):
    id = Inteiro, Chave Primaria
    nome = String(100), Nao Nulo
    descricao = Texto, Nao Nulo
    imagem_url = String(255), Nao Nulo # URL ou caminho da imagem do produto

classe Pedido(db.Model):
    id = Inteiro, Chave Primaria
    cliente_id = Inteiro, Chave Estrangeira(User.id), Nao Nulo
    detalhes_produto = Texto, Nao Nulo
    telefone_contato = String(20), Nao Nulo
    cep = String(9), Nao Nulo
    estado = String(2), Nao Nulo
    cidade = String(100), Nao Nulo
    endereco = String(255), Nao Nulo
    numero = String(10), Nao Nulo
    codigo_rastreio = String(50), Nulo # Modificável apenas por Atendentes
    status = String(30), Padrao='Pendente' # Transições: 'Pendente' -> 'Em Fabricação Manual' -> 'Enviado'
    data_criacao = DataHora, Padrao=agora()
4. Rotas e Lógica de Negócio (Controller)
/app/routes.py
ação: criar

descrição: Concentra o controle de rotas HTTP, validações de sessão e restrições com base no perfil (role) do usuário autenticado.

pseudocódigo:

Python
# SERVIÇO DE AUTENTICAÇÃO E CADASTRO BASE
rota GET '/':
    produtos = buscar_todos_os_produtos()
    renderizar 'home.html' passando produtos

rota GET/POST '/login':
    se requisicao == POST:
        extrair 'username' ou 'email' e 'password'
        usuario = buscar_usuario_por_username(username)
        se usuario existe e validar_hash(usuario.password_hash, password):
            login_user(usuario)
            redirecionar para rota base de acordo com usuario.role
        senao:
            retornar erro_autenticacao
    renderizar 'login.html'

rota POST '/cadastro':
    extrair dados de cadastro do cliente do formulário
    novo_cliente = User(username=username, password_hash=gerar_hash(senha), role='cliente')
    db.session.add(novo_cliente)
    db.session.commit()
    redirecionar '/login'

rota GET '/logout':
    logout_user()
    redirecionar '/'

# SERVIÇO DE PEDIDOS (EXCLUSIVO CLIENTE)
rota GET/POST '/clientes/pedidos':
    interceptar se current_user.role != 'cliente' -> abortar(403)
    se requisicao == POST:
        extrair 'detalhes_produto', 'telefone_contato', 'cep', 'estado', 'cidade', 'endereco', 'numero'
        novo_pedido = Pedido(cliente_id=current_user.id, detalhes_produto=detalhes_produto, telefone_contato=telefone_contato, cep=cep, estado=estado, cidade=cidade, endereco=endereco, numero=numero)
        db.session.add(novo_pedido)
        db.session.commit()

    pedidos_do_cliente = buscar_pedidos_onde(cliente_id == current_user.id)
    renderizar 'pedido_cliente.html' passando pedidos_do_cliente

rota POST '/clientes/pedidos/editar/<pedido_id>':
    interceptar se current_user.role != 'cliente' -> abortar(403)
    pedido = buscar_pedido_por_id(pedido_id)
    se pedido.cliente_id == current_user.id e pedido.status == 'Pendente':
        atualizar dados do pedido com dados do formulário
        db.session.commit()
    redirecionar '/clientes/pedidos'

rota POST '/clientes/pedidos/deletar/<pedido_id>':
    interceptar se current_user.role != 'cliente' -> abortar(403)
    pedido = buscar_pedido_por_id(pedido_id)
    se pedido.cliente_id == current_user.id e pedido.status == 'Pendente':
        deletar_do_banco(pedido)
        db.session.commit()
    redirecionar '/clientes/pedidos'

# SERVIÇO DE GESTÃO DE PEDIDOS (EXCLUSIVO ATENDENTE)
rota GET '/atendente/painel':
    interceptar se current_user.role != 'atendente' -> abortar(403)
    todos_pedidos = buscar_todos_os_pedidos()
    renderizar 'painel_atendente.html' passando todos_pedidos

rota POST '/atendente/iniciar_fabricacao/<pedido_id>':
    interceptar se current_user.role != 'atendente' -> abortar(403)
    pedido = buscar_pedido_por_id(pedido_id)
    pedido.status = 'Em Fabricação Manual'
    db.session.commit()
    redirecionar '/atendente/painel'

rota POST '/atendente/enviar_pedido/<pedido_id>':
    interceptar se current_user.role != 'atendente' -> abortar(403)
    codigo = extrair 'codigo_rastreio' do formulário
    pedido = buscar_pedido_por_id(pedido_id)
    pedido.status = 'Enviado'
    pedido.codigo_rastreio = codigo
    db.session.commit()
    redirecionar '/atendente/painel'

# SERVIÇO ADMINISTRATIVO (EXCLUSIVO ADMINISTRADOR)
rota GET/POST '/admin/atendentes':
    interceptar se current_user.role != 'admin' -> abortar(403)
    se requisicao == POST:
        extrair dados do atendente
        novo_atendente = User(username=username, password_hash=gerar_hash(senha), role='atendente')
        db.session.add(novo_atendente)
        db.session.commit()

    lista_atendentes = buscar_todos_usuarios_onde(role == 'atendente')
    renderizar 'crud_atendentes.html' passando lista_atendentes

rota POST '/admin/atendentes/deletar/<user_id>':
    interceptar se current_user.role != 'admin' -> abortar(403)
    usuario = buscar_usuario_por_id(user_id)
    deletar_do_banco(usuario)
    db.session.commit()
    redirecionar '/admin/atendentes'

rota GET/POST '/admin/produtos':
    interceptar se current_user.role != 'admin' -> abortar(403)
    se requisicao == POST:
        extrair 'nome', 'descricao', 'imagem_url'
        novo_produto = Produto(nome=nome, descricao=descricao, imagem_url=imagem_url)
        db.session.add(novo_produto)
        db.session.commit()
    
    lista_produtos = buscar_todos_os_produtos()
    renderizar 'crud_produtos.html' passando lista_produtos

rota POST '/admin/produtos/editar/<produto_id>':
    interceptar se current_user.role != 'admin' -> abortar(403)
    produto = buscar_produto_por_id(produto_id)
    atualizar produto com 'nome', 'descricao', 'imagem_url' do formulário
    db.session.commit()
    redirecionar '/admin/produtos'

rota POST '/admin/produtos/deletar/<produto_id>':
    interceptar se current_user.role != 'admin' -> abortar(403)
    produto = buscar_produto_por_id(produto_id)
    deletar_do_banco(produto)
    db.session.commit()
    redirecionar '/admin/produtos'

rota GET '/admin/relatorios':
    interceptar se current_user.role != 'admin' -> abortar(403)
    metricas = calcular_agrupamento_por_status_pedidos()
    todos_pedidos = buscar_todos_os_pedidos()
    renderizar 'relatorio_pedidos.html' passando metricas e todos_pedidos
5. Interface de Usuário (Templates Engine)
/app/templates/base.html
ação: criar

descrição: Template base estrutural do Jinja2 contendo a injeção do Bootstrap e navegação adaptável com base na sessão atual do usuário.

pseudocódigo:

HTML
<!DOCTYPE html>
Carregar CDN Bootstrap CSS
<html>
  <nav>
    Se current_user.is_authenticated:
        Se role == 'admin': exibir links [Atendentes, Relatórios]
        Se role == 'atendente': exibir links [Painel de Pedidos]
        Se role == 'cliente': exibir links [Meus Pedidos]
        Exibir link [Sair]
    Senao:
        Exibir links [Login, Cadastrar-se]
  </nav>
  <main class="container">
     Definir bloco 'content' dinâmico
  </main>
</html>
/app/templates/painel_atendente.html
ação: criar

descrição: Tela de gerenciamento operacional. Renderiza cartões ou tabelas de pedidos com botões de ação vinculados ao status atual do item.

pseudocódigo:

HTML
Estender 'base.html'
Bloco content:
    Para cada pedido em todos_pedidos:
        Renderizar dados do pedido (ID, Cliente, Detalhes, Status, Dados de Envio)
        Se status == 'Pendente':
            Exibir botão POST para '/atendente/iniciar_fabricacao/<pedido.id>' -> Label: "Iniciar Fabricação Manual"
        Se status == 'Em Fabricação Manual':
            Exibir formulário inline direcionado para '/atendente/enviar_pedido/<pedido.id>'
            Incluir campo de texto 'codigo_rastreio' (obrigatório)
            Exibir botão submit -> Label: "Despachar e Enviar"
/app/templates/relatorio_pedidos.html
ação: criar

descrição: Painel executivo para consolidação de estatísticas quantitativas dos pedidos gerados na aplicação e listagem detalhada.

pseudocódigo:

HTML
Estender 'base.html'
Bloco content:
    Exibir layout em Grid do Bootstrap:
        Card 1: Total Geral de Pedidos -> {{ metricas.total }}
        Card 2: Pedidos Aguardando -> {{ metricas.pendentes }}
        Card 3: Em Produção -> {{ metricas.em_fabricacao }}
        Card 4: Total Enviados -> {{ metricas.enviados }}

    Exibir Tabela de Pedidos:
        Para cada pedido em todos_pedidos:
            ID, Descrição (detalhes_produto), Status, Usuário (cliente.username)