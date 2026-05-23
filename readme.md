# Sistema de Encomenda de Produtos Artesanais Personalizados

Este é um sistema web desenvolvido em Flask para gestão de encomendas de produtos artesanais. O sistema conta com uma vitrine de produtos, área para clientes realizarem pedidos personalizados e painéis administrativos para atendentes e administradores.

## Funcionalidades

- **Vitrine (Home):** Exibição de produtos artesanais cadastrados pelo Administrador.
- **Área do Cliente:** Cadastro, login, realização de pedidos personalizados e gestão de pedidos (edição e deleção permitidas enquanto o pedido estiver com status 'Pendente').
- **Painel do Atendente:** Gestão do fluxo de produção (Pendente -> Em Fabricação -> Enviado) e inserção de código de rastreio.
- **Painel do Administrador:** Gestão de atendentes, gestão completa da vitrine (cadastro, edição e exclusão de produtos) e relatórios detalhados com dashboard e listagem de pedidos.
- **Auto-Seeding:** O sistema realiza o pré-cadastro automático de 5 produtos iniciais na primeira execução para facilitar a demonstração.
- **Interface Refinada:** Design responsivo, acessível e com feedback visual em tempo real (loading states, badges de status).

## Requisitos

- Python 3.9+
- Docker (opcional)

## Instalação

1. Clone o repositório.
2. Crie um ambiente virtual:
   ```bash
   python -m venv venv
   source venv/bin/activate
   ```
3. Instale as dependências:
   ```bash
   pip install -r requirements.txt
   ```
4. Configure as variáveis de ambiente no arquivo `.env`:
   ```text
   SECRET_KEY=sua_chave_secreta
   DATABASE_URL=sqlite:///database.db
   ADMIN_USERNAME=admin
   ADMIN_PASSWORD=admin
   ```

## Execução

Para rodar a aplicação:
```bash
python run.py
```
A aplicação estará disponível em `http://localhost:5000`.

## Testes

Para executar os testes automatizados:
```bash
PYTHONPATH=. pytest
```

## Docker

Para rodar via Docker:
```bash
docker build -t sistema-encomendas .
docker run -p 5000:5000 sistema-encomendas
```
