from flask import Blueprint, render_template, redirect, url_for, request
from flask_login import login_required, current_user
from ..services.order_service import OrderService
from ..utils.decorators import role_required
from ..utils.constants import UserRole

cliente_bp = Blueprint('cliente', __name__)

@cliente_bp.route('/clientes/pedidos', methods=['GET', 'POST'])
@login_required
@role_required(UserRole.CLIENTE)
def pedidos():
    if request.method == 'POST':
        OrderService.create_order(
            cliente_id=current_user.id,
            detalhes=request.form.get('detalhes_produto'),
            telefone=request.form.get('telefone_contato'),
            cep=request.form.get('cep'),
            estado=request.form.get('estado'),
            cidade=request.form.get('cidade'),
            endereco=request.form.get('endereco'),
            numero=request.form.get('numero')
        )
        return redirect(url_for('cliente.pedidos'))

    pedidos = OrderService.get_orders_by_client(current_user.id)
    return render_template('pedido_cliente.html', pedidos=pedidos)
