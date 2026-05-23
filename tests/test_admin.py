import pytest
from app.models import db, User, Pedido
from werkzeug.security import generate_password_hash

def test_crud_atendentes(app, client):
    with app.app_context():
        admin = User(username='admin_test', email='admin@test.com', 
                     password_hash=generate_password_hash('password'), role='admin')
        db.session.add(admin)
        db.session.commit()

    client.post('/login', data={'username': 'admin_test', 'password': 'password'})
    
    # Create atendente
    response = client.post('/admin/atendentes', data={
        'username': 'novo_atendente',
        'email': 'at@test.com',
        'password': 'password123'
    }, follow_redirects=True)
    assert response.status_code == 200
    assert b'novo_atendente' in response.data
    
    with app.app_context():
        atendente = User.query.filter_by(username='novo_atendente').first()
        assert atendente is not None
        assert atendente.role == 'atendente'
        atendente_id = atendente.id

    # Delete atendente
    response = client.post(f'/admin/atendentes/deletar/{atendente_id}', follow_redirects=True)
    assert response.status_code == 200
    assert b'novo_atendente' not in response.data
    
    with app.app_context():
        atendente = User.query.get(atendente_id)
        assert atendente is None

def test_relatorio_pedidos(app, client):
    with app.app_context():
        admin = User(username='admin_rel', email='adminrel@test.com', 
                     password_hash=generate_password_hash('password'), role='admin')
        cliente = User(username='cliente_rel', email='crel@test.com', 
                       password_hash=generate_password_hash('password'), role='cliente')
        db.session.add_all([admin, cliente])
        db.session.commit()
        
        p1 = Pedido(cliente_id=cliente.id, detalhes_produto='P1', dados_envio='D1', status='Pendente')
        p2 = Pedido(cliente_id=cliente.id, detalhes_produto='P2', dados_envio='D2', status='Em Fabricação Manual')
        p3 = Pedido(cliente_id=cliente.id, detalhes_produto='P3', dados_envio='D3', status='Enviado')
        db.session.add_all([p1, p2, p3])
        db.session.commit()

    client.post('/login', data={'username': 'admin_rel', 'password': 'password'})
    
    response = client.get('/admin/relatorios')
    assert response.status_code == 200
    assert b'3' in response.data # Total
    assert b'1' in response.data # Each status should have 1
