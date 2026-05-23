from flask import Blueprint, render_template, redirect, url_for, request
from flask_login import login_required
from ..services.order_service import OrderService
from ..utils.decorators import role_required
from ..utils.constants import UserRole, StatusPedido

atendente_bp = Blueprint('atendente', __name__)

@atendente_bp.route('/atendente/painel')
@login_required
@role_required(UserRole.ATENDENTE)
def painel():
    pedidos = OrderService.get_all_orders()
    return render_template('painel_atendente.html', pedidos=pedidos)

@atendente_bp.route('/atendente/iniciar_fabricacao/<int:pedido_id>', methods=['POST'])
@login_required
@role_required(UserRole.ATENDENTE)
def iniciar_fabricacao(pedido_id):
    OrderService.update_status(pedido_id, StatusPedido.EM_FABRICACAO)
    return redirect(url_for('atendente.painel'))

@atendente_bp.route('/atendente/enviar_pedido/<int:pedido_id>', methods=['POST'])
@login_required
@role_required(UserRole.ATENDENTE)
def enviar_pedido(pedido_id):
    codigo = request.form.get('codigo_rastreio')
    OrderService.update_status(pedido_id, StatusPedido.ENVIADO, codigo_rastreio=codigo)
    return redirect(url_for('atendente.painel'))
