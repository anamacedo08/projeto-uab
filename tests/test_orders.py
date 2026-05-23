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
        'dados_envio': 'Rua A, 123'
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
        
        pedido = Pedido(cliente_id=cliente.id, detalhes_produto='Bolsa Bordada', dados_envio='Rua B, 456')
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
