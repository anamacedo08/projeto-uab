import pytest
from app import create_app
from app.models import db, User

@pytest.fixture
def app():
    app = create_app()
    app.config.update({
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
        "WTF_CSRF_ENABLED": False,
        "SECRET_KEY": "test-key"
    })

    with app.app_context():
        db.create_all()
        yield app
        db.drop_all()

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def runner(app):
    return app.test_cli_runner()

@pytest.fixture
def auth_client(client, app):
    class AuthActions:
        def __init__(self, client):
            self._client = client

        def login(self, username='admin', password='password'):
            return self._client.post('/login', data={'username': username, 'password': password}, follow_redirects=True)

        def logout(self):
            return self._client.get('/logout', follow_redirects=True)

    return AuthActions(client)
