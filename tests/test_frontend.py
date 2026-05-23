import pytest
from app.models import db, User, Produto, Pedido
from werkzeug.security import generate_password_hash

def test_navbar_aria_current(app, client):
    """TC-23: Validar se o link da página atual no navbar possui aria-current='page'"""
    response = client.get('/')
    assert response.status_code == 200
    assert b'aria-current="page"' in response.data
    assert b'In\xc3\xadcio' in response.data # 'Início' encoded

def test_home_empty_state(app, client):
    """TC-26: Garantir exibição de mensagem 'Nenhum produto encontrado' quando a lista estiver vazia"""
    # Garantir que não há produtos
    with app.app_context():
        Produto.query.delete()
        db.session.commit()
        
    response = client.get('/')
    assert response.status_code == 200
    assert b'Nenhum produto em destaque no momento' in response.data

def test_pedido_status_badges(app, client):
    """TC-22: Garantir que o status 'Enviado' exiba badge verde e 'Pendente' exiba badge amarelo"""
    with app.app_context():
        cliente = User(username='cliente_test', email='ct@test.com', 
                      password_hash=generate_password_hash('password'), role='cliente')
        db.session.add(cliente)
        db.session.commit()
        
        p1 = Pedido(cliente_id=cliente.id, detalhes_produto='P1', status='Pendente', 
                    telefone_contato='123', cep='12345678', estado='SP', cidade='SP', endereco='Rua', numero='1')
        p2 = Pedido(cliente_id=cliente.id, detalhes_produto='P2', status='Enviado', 
                    telefone_contato='123', cep='12345678', estado='SP', cidade='SP', endereco='Rua', numero='1',
                    codigo_rastreio='ABC123456')
        db.session.add_all([p1, p2])
        db.session.commit()

    client.post('/login', data={'username': 'cliente_test', 'password': 'password'})
    response = client.get('/clientes/pedidos')
    
    assert response.status_code == 200
    # Pendente -> var(--secondary-color)
    assert b'style="background-color: var(--secondary-color); color: #fff;">Pendente</span>' in response.data
    # Enviado -> var(--success-color)
    assert b'style="background-color: var(--success-color); color: #fff;">Enviado</span>' in response.data

def test_logo_rendered(client):
    """TC-28: Confirmar se o novo logo SVG é renderizado correctly"""
    response = client.get('/')
    assert response.status_code == 200
    assert b'<svg width="32" height="32" viewBox="0 0 24 24" class="logo-icon"' in response.data
    assert b'ArtesaLab' in response.data

def test_product_actions_spacing(app, client):
    """TC-25: Validar se os botões de "Editar" e "Excluir" na tela de produtos possuem espaçamento (gap-2)"""
    with app.app_context():
        admin = User(username='admin_test', email='admin@test.com',
                    password_hash=generate_password_hash('password'), role='admin')
        db.session.add(admin)
        p = Produto(nome='P1', descricao='D1', imagem_url='http://img.com')
        db.session.add(p)
        db.session.commit()

    client.post('/login', data={'username': 'admin_test', 'password': 'password'})
    response = client.get('/admin/produtos')
    assert response.status_code == 200
    assert b'd-flex justify-content-center gap-2' in response.data

def test_form_validation_attributes(app, client):
    """TC-25: Verificar se a validação HTML5 (pattern para CEP) está presente"""
    with app.app_context():
        cliente = User(username='cliente_val', email='cv@test.com', 
                      password_hash=generate_password_hash('password'), role='cliente')
        db.session.add(cliente)
        db.session.commit()

    client.post('/login', data={'username': 'cliente_val', 'password': 'password'})
    response = client.get('/clientes/pedidos')
    
    assert response.status_code == 200
    assert b'pattern="[0-9]{5}-?[0-9]{3}"' in response.data
    assert b'required' in response.data

def test_table_responsiveness(app, client):
    """TC-21: Verificar se as tabelas possuem .table-responsive"""
    with app.app_context():
        cliente = User(username='cliente_resp', email='cr@test.com', 
                      password_hash=generate_password_hash('password'), role='cliente')
        db.session.add(cliente)
        db.session.commit()

    client.post('/login', data={'username': 'cliente_resp', 'password': 'password'})
    response = client.get('/clientes/pedidos')
    assert b'table-responsive' in response.data

def test_accessibility_labels(app, client):
    """TC-24: Verificar se os inputs possuem labels associados"""
    response = client.get('/login')
    assert b'for="username"' in response.data
    assert b'id="username"' in response.data
    assert b'for="password"' in response.data
    assert b'id="password"' in response.data
