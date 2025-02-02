from flask import Blueprint, render_template
from flask_login import login_required
from app.models import Veiculo

bp = Blueprint('relatorios', __name__)

@bp.route('/')
@login_required
def index():
    veiculos = Veiculo.query.all()
    return render_template('relatorios.html', veiculos=veiculos) 