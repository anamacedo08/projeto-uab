import pytest
from app.models import db, User, Produto
from werkzeug.security import generate_password_hash

def test_home_page_vitrine(app, client):
    with app.app_context():
        p1 = Produto(nome='Produto 1', descricao='Desc 1', imagem_url='http://img1.jpg')
        p2 = Produto(nome='Produto 2', descricao='Desc 2', imagem_url='http://img2.jpg')
        db.session.add_all([p1, p2])
        db.session.commit()

    response = client.get('/')
    assert response.status_code == 200
    assert b'Produto 1' in response.data
    assert b'Produto 2' in response.data
    assert b'Desc 1' in response.data
    assert b'Login' in response.data

def test_admin_crud_produtos(app, client):
    with app.app_context():
        admin = User(username='admin_prod', email='ap@test.com', 
                    password_hash=generate_password_hash('password'), role='admin')
        db.session.add(admin)
        db.session.commit()

    client.post('/login', data={'username': 'admin_prod', 'password': 'password'})
    
    # Criar produto
    response = client.post('/admin/produtos', data={
        'nome': 'Novo Artesanato',
        'descricao': 'Uma peça única',
        'imagem_url': 'http://img.com/peca.jpg'
    }, follow_redirects=True)
    
    assert response.status_code == 200
    assert b'Novo Artesanato' in response.data
    
    with app.app_context():
        prod = Produto.query.filter_by(nome='Novo Artesanato').first()
        assert prod is not None
        prod_id = prod.id

    # Deletar produto
    response = client.post(f'/admin/produtos/deletar/{prod_id}', follow_redirects=True)
    assert response.status_code == 200
    assert b'Novo Artesanato' not in response.data
    
    with app.app_context():
        prod = Produto.query.get(prod_id)
        assert prod is None
