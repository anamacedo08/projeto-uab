from flask import Blueprint, render_template, redirect, url_for, request
from flask_login import login_required
from ..services.user_service import UserService
from ..services.product_service import ProductService
from ..services.order_service import OrderService
from ..utils.decorators import role_required
from ..utils.constants import UserRole

admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/admin/atendentes', methods=['GET', 'POST'])
@login_required
@role_required(UserRole.ADMIN)
def atendentes():
    if request.method == 'POST':
        UserService.create_user(
            username=request.form.get('username'),
            email=request.form.get('email'),
            password=request.form.get('password'),
            role=UserRole.ATENDENTE
        )
        return redirect(url_for('admin.atendentes'))

    atendentes = UserService.get_atendentes()
    return render_template('crud_atendentes.html', atendentes=atendentes)

@admin_bp.route('/admin/atendentes/deletar/<int:user_id>', methods=['POST'])
@login_required
@role_required(UserRole.ADMIN)
def deletar_atendente(user_id):
    UserService.delete_user(user_id)
    return redirect(url_for('admin.atendentes'))

@admin_bp.route('/admin/relatorios')
@login_required
@role_required(UserRole.ADMIN)
def relatorios():
    metricas = OrderService.get_metrics()
    todos_pedidos = OrderService.get_all_orders()
    return render_template('relatorio_pedidos.html', metricas=metricas, todos_pedidos=todos_pedidos)

@admin_bp.route('/admin/produtos', methods=['GET', 'POST'])
@login_required
@role_required(UserRole.ADMIN)
def produtos():
    if request.method == 'POST':
        ProductService.create_product(
            nome=request.form.get('nome'),
            descricao=request.form.get('descricao'),
            imagem_url=request.form.get('imagem_url')
        )
        return redirect(url_for('admin.produtos'))

    produtos = ProductService.get_all_products()
    return render_template('crud_produtos.html', produtos=produtos)

@admin_bp.route('/admin/produtos/editar/<int:produto_id>', methods=['POST'])
@login_required
@role_required(UserRole.ADMIN)
def editar_produto(produto_id):
    ProductService.update_product(
        produto_id=produto_id,
        nome=request.form.get('nome'),
        descricao=request.form.get('descricao'),
        imagem_url=request.form.get('imagem_url')
    )
    return redirect(url_for('admin.produtos'))

@admin_bp.route('/admin/produtos/deletar/<int:produto_id>', methods=['POST'])
@login_required
@role_required(UserRole.ADMIN)
def deletar_produto(produto_id):
    ProductService.delete_product(produto_id)
    return redirect(url_for('admin.produtos'))
