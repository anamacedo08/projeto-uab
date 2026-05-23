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

class Produto(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    descricao = db.Column(db.Text, nullable=False)
    imagem_url = db.Column(db.String(255), nullable=False)

class Pedido(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    cliente_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    detalhes_produto = db.Column(db.Text, nullable=False)
    telefone_contato = db.Column(db.String(20), nullable=False)
    cep = db.Column(db.String(9), nullable=False)
    estado = db.Column(db.String(2), nullable=False)
    cidade = db.Column(db.String(100), nullable=False)
    endereco = db.Column(db.String(255), nullable=False)
    numero = db.Column(db.String(10), nullable=False)
    codigo_rastreio = db.Column(db.String(50), nullable=True)
    status = db.Column(db.String(30), default='Pendente')
    data_criacao = db.Column(db.DateTime, default=datetime.utcnow)

    cliente = db.relationship('User', backref=db.backref('pedidos', lazy=True))
