from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime

db = SQLAlchemy()

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    role = db.Column(db.String(20), nullable=False)  # 'admin', 'atendente', 'cliente'

class Pedido(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    cliente_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    detalhes_produto = db.Column(db.Text, nullable=False)
    dados_envio = db.Column(db.Text, nullable=False)
    codigo_rastreio = db.Column(db.String(50), nullable=True)
    status = db.Column(db.String(30), default='Pendente')
    data_criacao = db.Column(db.DateTime, default=datetime.utcnow)

    cliente = db.relationship('User', backref=db.backref('pedidos', lazy=True))
