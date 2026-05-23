import pytest
from app.models import db, User, Pedido
from werkzeug.security import generate_password_hash

def test_criacao_pedido(app, client):
    with app.app_context():
        user = User(username='cliente_pedidos', email='cp@test.com', 
                    password_hash=generate_password_hash('password'), role='cliente')
        db.session.add(user)
        db.session.commit()

    client.post('/login', data={'username': 'cliente_pedidos', 'password': 'password'})
    
    response = client.post('/clientes/pedidos', data={
        'detalhes_produto': 'Vaso de Cerâmica',
        'telefone_contato': '11999999999',
        'cep': '01001-000',
        'estado': 'SP',
        'cidade': 'São Paulo',
        'endereco': 'Praça da Sé',
        'numero': 'S/N'
    }, follow_redirects=True)
    
    assert response.status_code == 200
    assert b'Vaso de Cer\xc3\xa2mica' in response.data
    
    with app.app_context():
        pedido = Pedido.query.filter_by(detalhes_produto='Vaso de Cerâmica').first()
        assert pedido is not None
        assert pedido.status == 'Pendente'

def test_fluxo_pedido_atendente(app, client):
    with app.app_context():
        cliente = User(username='cliente_fluxo', email='cf@test.com', 
                       password_hash=generate_password_hash('password'), role='cliente')
        atendente = User(username='atendente_fluxo', email='af@test.com', 
                         password_hash=generate_password_hash('password'), role='atendente')
        db.session.add_all([cliente, atendente])
        db.session.commit()
        
        pedido = Pedido(
            cliente_id=cliente.id, 
            detalhes_produto='Bolsa Bordada', 
            telefone_contato='11888888888',
            cep='01001-000',
            estado='SP',
            cidade='São Paulo',
            endereco='Rua B',
            numero='456'
        )
        db.session.add(pedido)
        db.session.commit()
        pedido_id = pedido.id

    # Login as atendente
    client.post('/login', data={'username': 'atendente_fluxo', 'password': 'password'})
    
    # Iniciar fabricação
    response = client.post(f'/atendente/iniciar_fabricacao/{pedido_id}', follow_redirects=True)
    assert response.status_code == 200
    with app.app_context():
        pedido = Pedido.query.get(pedido_id)
        assert pedido.status == 'Em Fabricação Manual'
    
    # Enviar pedido
    response = client.post(f'/atendente/enviar_pedido/{pedido_id}', data={
        'codigo_rastreio': 'BR123456789'
    }, follow_redirects=True)
    assert response.status_code == 200
    with app.app_context():
        pedido = Pedido.query.get(pedido_id)
        assert pedido.status == 'Enviado'
        assert pedido.codigo_rastreio == 'BR123456789'

def test_editar_pedido(app, client):
    with app.app_context():
        user = User(username='cliente_edit', email='ce@test.com', 
                    password_hash=generate_password_hash('password'), role='cliente')
        db.session.add(user)
        db.session.commit()
        
        pedido = Pedido(
            cliente_id=user.id, 
            detalhes_produto='Pedido Antigo', 
            telefone_contato='11777777777',
            cep='01001-000',
            estado='SP',
            cidade='São Paulo',
            endereco='Rua C',
            numero='789'
        )
        db.session.add(pedido)
        db.session.commit()
        pedido_id = pedido.id

    client.post('/login', data={'username': 'cliente_edit', 'password': 'password'})
    
    response = client.post(f'/clientes/pedidos/editar/{pedido_id}', data={
        'detalhes_produto': 'Pedido Atualizado',
        'telefone_contato': '11666666666',
        'cep': '02002-000',
        'estado': 'RJ',
        'cidade': 'Rio de Janeiro',
        'endereco': 'Rua D',
        'numero': '123'
    }, follow_redirects=True)
    
    assert response.status_code == 200
    assert b'Pedido Atualizado' in response.data
    
    with app.app_context():
        pedido = Pedido.query.get(pedido_id)
        assert pedido.detalhes_produto == 'Pedido Atualizado'
        assert pedido.cidade == 'Rio de Janeiro'

def test_deletar_pedido(app, client):
    with app.app_context():
        user = User(username='cliente_del', email='cdel@test.com', 
                    password_hash=generate_password_hash('password'), role='cliente')
        db.session.add(user)
        db.session.commit()
        
        pedido = Pedido(
            cliente_id=user.id, 
            detalhes_produto='Pedido para Deletar', 
            telefone_contato='11555555555',
            cep='01001-000',
            estado='SP',
            cidade='São Paulo',
            endereco='Rua E',
            numero='000'
        )
        db.session.add(pedido)
        db.session.commit()
        pedido_id = pedido.id

    client.post('/login', data={'username': 'cliente_del', 'password': 'password'})
    
    response = client.post(f'/clientes/pedidos/deletar/{pedido_id}', follow_redirects=True)
    
    assert response.status_code == 200
    assert b'Pedido para Deletar' not in response.data
    
    with app.app_context():
        pedido = Pedido.query.get(pedido_id)
        assert pedido is None

def test_bloqueio_edicao_pedido_em_fabricacao(app, client):
    with app.app_context():
        user = User(username='cliente_block', email='cb@test.com', 
                    password_hash=generate_password_hash('password'), role='cliente')
        db.session.add(user)
        db.session.commit()
        
        pedido = Pedido(
            cliente_id=user.id, 
            detalhes_produto='Pedido Intocável', 
            telefone_contato='11444444444',
            cep='01001-000',
            estado='SP',
            cidade='São Paulo',
            endereco='Rua F',
            numero='111',
            status='Em Fabricação Manual'
        )
        db.session.add(pedido)
        db.session.commit()
        pedido_id = pedido.id

    client.post('/login', data={'username': 'cliente_block', 'password': 'password'})
    
    # Tenta editar
    client.post(f'/clientes/pedidos/editar/{pedido_id}', data={
        'detalhes_produto': 'Tentativa de Edição',
        'telefone_contato': '11444444444',
        'cep': '01001-000',
        'estado': 'SP',
        'cidade': 'São Paulo',
        'endereco': 'Rua F',
        'numero': '111'
    })
    
    with app.app_context():
        pedido = Pedido.query.get(pedido_id)
        assert pedido.detalhes_produto == 'Pedido Intocável' # Não deve mudar
    
    # Tenta deletar
    client.post(f'/clientes/pedidos/deletar/{pedido_id}')
    
    with app.app_context():
        pedido = Pedido.query.get(pedido_id)
        assert pedido is not None # Não deve deletar
