from flask import Blueprint, render_template
from ..services.product_service import ProductService

public_bp = Blueprint('public', __name__)

@public_bp.route('/')
def home():
    produtos = ProductService.get_all_products()
    return render_template('home.html', produtos=produtos)
