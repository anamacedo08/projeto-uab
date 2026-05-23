# Sistema de Encomenda de Produtos Artesanais Personalizados

Este é um sistema web desenvolvido em Flask para gestão de encomendas de produtos artesanais.

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
pytest
```

## Docker

Para rodar via Docker:
```bash
docker build -t sistema-encomendas .
docker run -p 5000:5000 sistema-encomendas
```
