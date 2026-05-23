from werkzeug.security import generate_password_hash
from ..models import db, User
from ..utils.constants import UserRole

class UserService:
    @staticmethod
    def create_user(username, email, password, role):
        novo_usuario = User(
            username=username,
            email=email,
            password_hash=generate_password_hash(password),
            role=role
        )
        db.session.add(novo_usuario)
        db.session.commit()
        return novo_usuario

    @staticmethod
    def get_atendentes():
        return User.query.filter_by(role=UserRole.ATENDENTE).all()

    @staticmethod
    def delete_user(user_id):
        usuario = User.query.get(user_id)
        if usuario:
            db.session.delete(usuario)
            db.session.commit()
            return True
        return False

    @staticmethod
    def get_user_by_id(user_id):
        return User.query.get(user_id)
