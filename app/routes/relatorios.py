from flask import render_template, Blueprint
from flask_login import login_required

bp = Blueprint('relatorios', __name__)

@bp.route('/')
@login_required
def index():
    return render_template('relatorios.html')

@bp.route('/gerar', methods=['POST'])
@login_required
def gerar_relatorio():
    # Implementar a geração do relatório
    return "Relatório será implementado em breve" 