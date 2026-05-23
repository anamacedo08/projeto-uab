import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from werkzeug.security import generate_password_hash
from dotenv import load_dotenv

load_dotenv()

from .models import db, User

login_manager = LoginManager()

def create_app():
    app = Flask(__name__)
    
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'default-key')
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///database.db')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'main.login'

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    from .routes import main
    app.register_blueprint(main)

    with app.app_context():
        db.create_all()


        admin_user = os.getenv('ADMIN_USERNAME')
        admin_pass = os.getenv('ADMIN_PASSWORD')

        if not User.query.filter_by(username=admin_user).first():
            new_admin = User(
                username=admin_user,
                email='admin@example.com',
                password_hash=generate_password_hash(admin_pass),
                role='admin'
            )
            db.session.add(new_admin)
            db.session.commit()

    return app
