import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_caching import Cache
from flask_executor import Executor
from werkzeug.security import generate_password_hash
from dotenv import load_dotenv

load_dotenv()

from .models import db, User
from .utils.constants import UserRole

login_manager = LoginManager()
cache = Cache()
executor = Executor()

def create_app():
    app = Flask(__name__)
    
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'default-key')
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///database.db')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # Cache Config
    app.config['CACHE_TYPE'] = 'SimpleCache'
    app.config['CACHE_DEFAULT_TIMEOUT'] = 300

    db.init_app(app)
    login_manager.init_app(app)
    cache.init_app(app)
    executor.init_app(app)
    
    login_manager.login_view = 'auth.login'

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # Register Blueprints
    from .routes.auth import auth_bp
    from .routes.admin import admin_bp
    from .routes.atendente import atendente_bp
    from .routes.cliente import cliente_bp
    from .routes.public import public_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(atendente_bp)
    app.register_blueprint(cliente_bp)
    app.register_blueprint(public_bp)

    with app.app_context():
        db.create_all()

        admin_user = os.getenv('ADMIN_USERNAME')
        admin_pass = os.getenv('ADMIN_PASSWORD')

        if admin_user and not User.query.filter_by(username=admin_user).first():
            new_admin = User(
                username=admin_user,
                email='admin@example.com',
                password_hash=generate_password_hash(admin_pass),
                role=UserRole.ADMIN
            )
            db.session.add(new_admin)
            db.session.commit()

    return app
