import time
from ..models import db, Pedido
from ..utils.constants import StatusPedido
from .. import cache, executor

def send_status_notification(pedido_id, status):
    # Simula um processamento pesado de notificação (ex: email, webhook)
    time.sleep(2)
    print(f"NOTIFICAÇÃO: Pedido {pedido_id} alterado para {status}")

class OrderService:
    @staticmethod
    def create_order(cliente_id, detalhes, telefone, cep, estado, cidade, endereco, numero):
        novo_pedido = Pedido(
            cliente_id=cliente_id,
            detalhes_produto=detalhes,
            telefone_contato=telefone,
            cep=cep,
            estado=estado,
            cidade=cidade,
            endereco=endereco,
            numero=numero
        )
        db.session.add(novo_pedido)
        db.session.commit()
        cache.delete('order_metrics')
        return novo_pedido

    @staticmethod
    def update_order(pedido_id, cliente_id, detalhes, telefone, cep, estado, cidade, endereco, numero):
        pedido = Pedido.query.get(pedido_id)
        if pedido and pedido.cliente_id == cliente_id and pedido.status == StatusPedido.PENDENTE:
            pedido.detalhes_produto = detalhes
            pedido.telefone_contato = telefone
            pedido.cep = cep
            pedido.estado = estado
            pedido.cidade = cidade
            pedido.endereco = endereco
            pedido.numero = numero
            db.session.commit()
            cache.delete('order_metrics')
            return pedido
        return None

    @staticmethod
    def delete_order(pedido_id, cliente_id):
        pedido = Pedido.query.get(pedido_id)
        if pedido and pedido.cliente_id == cliente_id and pedido.status == StatusPedido.PENDENTE:
            db.session.delete(pedido)
            db.session.commit()
            cache.delete('order_metrics')
            return True
        return False

    @staticmethod
    def get_orders_by_client(cliente_id):
        return Pedido.query.filter_by(cliente_id=cliente_id).all()

    @staticmethod
    def get_all_orders():
        return Pedido.query.all()

    @staticmethod
    def update_status(pedido_id, status, codigo_rastreio=None):
        pedido = Pedido.query.get(pedido_id)
        if pedido:
            pedido.status = status
            if codigo_rastreio:
                pedido.codigo_rastreio = codigo_rastreio
            db.session.commit()
            
            # Invalida cache de métricas
            cache.delete('order_metrics')
            
            # Dispara job em background
            executor.submit(send_status_notification, pedido_id, status)
            return True
        return False

    @staticmethod
    @cache.cached(timeout=120, key_prefix='order_metrics')
    def get_metrics():
        total = Pedido.query.count()
        pendentes = Pedido.query.filter_by(status=StatusPedido.PENDENTE).count()
        em_fabricacao = Pedido.query.filter_by(status=StatusPedido.EM_FABRICACAO).count()
        enviados = Pedido.query.filter_by(status=StatusPedido.ENVIADO).count()
        
        return {
            'total': total,
            'pendentes': pendentes,
            'em_fabricacao': em_fabricacao,
            'enviados': enviados
        }
