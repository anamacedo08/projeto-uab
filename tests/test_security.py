import pytest
from app.models import db, User
from werkzeug.security import generate_password_hash

def setup_user(app, username, role):
    with app.app_context():
        user = User(username=username, email=f'{username}@test.com', 
                    password_hash=generate_password_hash('password'), role=role)
        db.session.add(user)
        db.session.commit()
        return user.id

def test_cliente_access_atendente_panel(app, client):
    setup_user(app, 'cliente1', 'cliente')
    client.post('/login', data={'username': 'cliente1', 'password': 'password'})
    
    response = client.get('/atendente/painel')
    assert response.status_code == 403

def test_cliente_access_admin_atendentes(app, client):
    setup_user(app, 'cliente2', 'cliente')
    client.post('/login', data={'username': 'cliente2', 'password': 'password'})
    
    response = client.get('/admin/atendentes')
    assert response.status_code == 403

def test_atendente_access_admin_atendentes(app, client):
    setup_user(app, 'atendente1', 'atendente')
    client.post('/login', data={'username': 'atendente1', 'password': 'password'})
    
    response = client.get('/admin/atendentes')
    assert response.status_code == 403
