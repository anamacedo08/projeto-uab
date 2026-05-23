from ..models import db, Produto
from .. import cache

class ProductService:
    @staticmethod
    @cache.cached(timeout=60, key_prefix='all_products')
    def get_all_products():
        return Produto.query.all()

    @staticmethod
    def create_product(nome, descricao, imagem_url):
        novo_produto = Produto(
            nome=nome,
            descricao=descricao,
            imagem_url=imagem_url
        )
        db.session.add(novo_produto)
        db.session.commit()
        cache.delete('all_products')
        return novo_produto

    @staticmethod
    def delete_product(produto_id):
        produto = Produto.query.get(produto_id)
        if produto:
            db.session.delete(produto)
            db.session.commit()
            cache.delete('all_products')
            return True
        return False
