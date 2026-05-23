from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_user, logout_user, login_required
from werkzeug.security import generate_password_hash, check_password_hash
from ..models import db, User
from ..utils.constants import UserRole

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter((User.username == username) | (User.email == username)).first()
        if user and check_password_hash(user.password_hash, password):
            login_user(user)
            if user.role == UserRole.ADMIN:
                return redirect(url_for('admin.atendentes'))
            elif user.role == UserRole.ATENDENTE:
                return redirect(url_for('atendente.painel'))
            else:
                return redirect(url_for('cliente.pedidos'))
        else:
            flash('Erro de autenticação. Verifique seus dados.')
    return render_template('login.html')

@auth_bp.route('/cadastro', methods=['POST'])
def cadastro():
    username = request.form.get('username')
    email = request.form.get('email')
    password = request.form.get('password')
    
    if User.query.filter_by(username=username).first():
        flash('Username já existe.')
        return redirect(url_for('auth.login'))
        
    novo_cliente = User(
        username=username, 
        email=email,
        password_hash=generate_password_hash(password), 
        role=UserRole.CLIENTE
    )
    db.session.add(novo_cliente)
    db.session.commit()
    return redirect(url_for('auth.login'))

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('public.home'))
