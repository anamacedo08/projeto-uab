from flask import Blueprint, render_template, redirect, url_for, request, flash, abort
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from .models import db, User, Pedido

main = Blueprint('main', __name__)

@main.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter((User.username == username) | (User.email == username)).first()
        if user and check_password_hash(user.password_hash, password):
            login_user(user)
            if user.role == 'admin':
                return redirect(url_for('main.admin_atendentes'))
            elif user.role == 'atendente':
                return redirect(url_for('main.atendente_painel'))
            else:
                return redirect(url_for('main.cliente_pedidos'))
        else:
            flash('Erro de autenticação. Verifique seus dados.')
    return render_template('login.html')

@main.route('/cadastro', methods=['POST'])
def cadastro():
    username = request.form.get('username')
    email = request.form.get('email')
    password = request.form.get('password')
    
    if User.query.filter_by(username=username).first():
        flash('Username já existe.')
        return redirect(url_for('main.login'))
        
    novo_cliente = User(
        username=username, 
        email=email,
        password_hash=generate_password_hash(password), 
        role='cliente'
    )
    db.session.add(novo_cliente)
    db.session.commit()
    return redirect(url_for('main.login'))

@main.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.login'))

# SERVIÇO DE PEDIDOS (EXCLUSIVO CLIENTE)
@main.route('/clientes/pedidos', methods=['GET', 'POST'])
@login_required
def cliente_pedidos():
    if current_user.role != 'cliente':
        abort(403)
    if request.method == 'POST':
        detalhes = request.form.get('detalhes_produto')
        envio = request.form.get('dados_envio')
        novo_pedido = Pedido(cliente_id=current_user.id, detalhes_produto=detalhes, dados_envio=envio)
        db.session.add(novo_pedido)
        db.session.commit()
        return redirect(url_for('main.cliente_pedidos'))

    pedidos = Pedido.query.filter_by(cliente_id=current_user.id).all()
    return render_template('pedido_cliente.html', pedidos=pedidos)

# SERVIÇO DE GESTÃO DE PEDIDOS (EXCLUSIVO ATENDENTE)
@main.route('/atendente/painel')
@login_required
def atendente_painel():
    if current_user.role != 'atendente':
        abort(403)
    pedidos = Pedido.query.all()
    return render_template('painel_atendente.html', pedidos=pedidos)

@main.route('/atendente/iniciar_fabricacao/<int:pedido_id>', methods=['POST'])
@login_required
def iniciar_fabricacao(pedido_id):
    if current_user.role != 'atendente':
        abort(403)
    pedido = Pedido.query.get_or_404(pedido_id)
    pedido.status = 'Em Fabricação Manual'
    db.session.commit()
    return redirect(url_for('main.atendente_painel'))

@main.route('/atendente/enviar_pedido/<int:pedido_id>', methods=['POST'])
@login_required
def enviar_pedido(pedido_id):
    if current_user.role != 'atendente':
        abort(403)
    codigo = request.form.get('codigo_rastreio')
    pedido = Pedido.query.get_or_404(pedido_id)
    pedido.status = 'Enviado'
    pedido.codigo_rastreio = codigo
    db.session.commit()
    return redirect(url_for('main.atendente_painel'))

# SERVIÇO ADMINISTRATIVO (EXCLUSIVO ADMINISTRADOR)
@main.route('/admin/atendentes', methods=['GET', 'POST'])
@login_required
def admin_atendentes():
    if current_user.role != 'admin':
        abort(403)
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        novo_atendente = User(
            username=username, 
            email=email,
            password_hash=generate_password_hash(password), 
            role='atendente'
        )
        db.session.add(novo_atendente)
        db.session.commit()
        return redirect(url_for('main.admin_atendentes'))

    atendentes = User.query.filter_by(role='atendente').all()
    return render_template('crud_atendentes.html', atendentes=atendentes)

@main.route('/admin/atendentes/deletar/<int:user_id>', methods=['POST'])
@login_required
def deletar_atendente(user_id):
    if current_user.role != 'admin':
        abort(403)
    usuario = User.query.get_or_404(user_id)
    db.session.delete(usuario)
    db.session.commit()
    return redirect(url_for('main.admin_atendentes'))

@main.route('/admin/relatorios')
@login_required
def admin_relatorios():
    if current_user.role != 'admin':
        abort(403)
    
    total = Pedido.query.count()
    pendentes = Pedido.query.filter_by(status='Pendente').count()
    em_fabricacao = Pedido.query.filter_by(status='Em Fabricação Manual').count()
    enviados = Pedido.query.filter_by(status='Enviado').count()
    
    metricas = {
        'total': total,
        'pendentes': pendentes,
        'em_fabricacao': em_fabricacao,
        'enviados': enviados
    }
    return render_template('relatorio_pedidos.html', metricas=metricas)

@main.route('/')
def index():
    return redirect(url_for('main.login'))

