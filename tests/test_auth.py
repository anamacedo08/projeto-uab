import pytest
from app.models import db, User
from werkzeug.security import generate_password_hash

def test_cadastro_cliente(app, client):
    response = client.post('/cadastro', data={
        'username': 'novo_cliente',
        'email': 'cliente@test.com',
        'password': 'password123'
    }, follow_redirects=True)
    
    assert response.status_code == 200
    with app.app_context():
        user = User.query.filter_by(username='novo_cliente').first()
        assert user is not None
        assert user.role == 'cliente'
        assert user.email == 'cliente@test.com'

def test_login_logout(app, client):
    with app.app_context():
        user = User(username='testuser', email='test@test.com', 
                    password_hash=generate_password_hash('testpass'), role='cliente')
        db.session.add(user)
        db.session.commit()

    # Login
    response = client.post('/login', data={
        'username': 'testuser',
        'password': 'testpass'
    }, follow_redirects=True)
    assert response.status_code == 200
    assert b'Meus Pedidos' in response.data

    # Logout
    response = client.get('/logout', follow_redirects=True)
    assert response.status_code == 200
    assert b'Login' in response.data

def test_acesso_nao_autenticado(client):
    response = client.get('/clientes/pedidos')
    assert response.status_code == 302
    assert '/login' in response.location
