# Especificação Técnica do Sistema (03-especs.md)

Este documento detalha a arquitetura e especificações técnicas do Sistema de Encomenda de Produtos Artesanais Personalizados, incluindo as otimizações de performance e modularização.

---

## 1. Arquitetura do Sistema
O sistema segue o padrão **MVC (Model-View-Controller)** com uma camada adicional de **Serviços** para isolar a lógica de negócio.

- **Camada de Dados (Models):** SQLAlchemy para mapeamento objeto-relacional.
- **Camada de Serviços (Services):** Centraliza a lógica de negócio, interações com o DB, Cache e disparo de Jobs.
- **Camada de Controle (Routes/Blueprints):** Gerencia as requisições HTTP e delega as ações para os Serviços.
- **Otimização:** 
    - **Cache:** Flask-Caching para rotas de leitura intensa (Home e Relatórios).
    - **Background Jobs:** Flask-Executor para processamento assíncrono (Notificações de status).

---

## 2. Camada de Serviços (Business Logic)

### `app/services/product_service.py`
- `get_all_products()`: Retorna todos os produtos (Cached: 60s).
- `create_product(nome, descricao, imagem_url)`: Cria produto e limpa cache.
- `delete_product(produto_id)`: Remove produto e limpa cache.

### `app/services/user_service.py`
- `create_user(username, email, password, role)`: Cria usuário (Admin/Atendente/Cliente).
- `get_atendentes()`: Lista usuários com role 'atendente'.
- `delete_user(user_id)`: Remove usuário do sistema.

### `app/services/order_service.py`
- `create_order(...)`: Registra novo pedido e limpa cache de métricas.
- `get_orders_by_client(cliente_id)`: Lista pedidos de um cliente específico.
- `get_all_orders()`: Lista todos os pedidos (para Atendentes).
- `update_status(pedido_id, status, codigo_rastreio)`: Atualiza status do pedido, limpa cache e dispara **Background Job** de notificação.
- `get_metrics()`: Calcula estatísticas de pedidos (Cached: 120s).

---

## 3. Inicialização e Configuração
### `/app/__init__.py`
- Inicializa extensões: `SQLAlchemy`, `LoginManager`, `Cache`, `Executor`.
- Configura o Administrador padrão via variáveis de ambiente.

... (restante dos arquivos de configuração como Dockerfile e requirements permanecem conforme anterior)
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

rota POST '/admin/produtos/deletar/<produto_id>':
    interceptar se current_user.role != 'admin' -> abortar(403)
    produto = buscar_produto_por_id(produto_id)
    deletar_do_banco(produto)
    db.session.commit()
    redirecionar '/admin/produtos'

rota GET '/admin/relatorios':
    interceptar se current_user.role != 'admin' -> abortar(403)
    metricas = calcular_agrupamento_por_status_pedidos()
    renderizar 'relatorio_pedidos.html' passando metricas
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

descrição: Painel executivo para consolidação de estatísticas quantitativas dos pedidos gerados na aplicação.

pseudocódigo:

HTML
Estender 'base.html'
Bloco content:
    Exibir layout em Grid do Bootstrap:
        Card 1: Total Geral de Pedidos -> {{ metricas.total }}
        Card 2: Pedidos Aguardando -> {{ metricas.pendentes }}
        Card 3: Em Produção -> {{ metricas.em_fabricacao }}
        Card 4: Total Enviados -> {{ metricas.enviados }}