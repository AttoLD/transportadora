from flask import Flask, render_template, request, jsonify, redirect, url_for
from models import db, Veiculo, ControleDiario, Movimento, Despesa
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///transportadora.db'
db.init_app(app)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/iniciar-dia', methods=['GET', 'POST'])
def iniciar_dia():
    if request.method == 'POST':
        data = request.form
        controle = ControleDiario(
            data=datetime.strptime(data['data'], '%Y-%m-%d'),
            veiculo_id=data['veiculo'],
            km_inicial=data['km_inicial']
        )
        db.session.add(controle)
        db.session.commit()
        return redirect(url_for('movimentos', controle_id=controle.id))
    
    veiculos = Veiculo.query.all()
    return render_template('iniciar_dia.html', veiculos=veiculos)

@app.route('/movimentos/<int:controle_id>', methods=['GET', 'POST'])
def movimentos(controle_id):
    controle = ControleDiario.query.get_or_404(controle_id)
    if request.method == 'POST':
        data = request.form
        movimento = Movimento(
            data=controle.data,
            controle_id=controle_id,
            cliente=data['cliente'],
            tipo_servico=data['tipo_servico'],
            descricao=data['descricao'],
            valor=float(data['valor']),
            forma_pagamento=data['forma_pagamento']
        )
        db.session.add(movimento)
        db.session.commit()
        return jsonify({'status': 'success'})
    
    movimentos = Movimento.query.filter_by(controle_id=controle_id).all()
    return render_template('movimentos.html', controle=controle, movimentos=movimentos)

@app.route('/finalizar-dia/<int:controle_id>', methods=['POST'])
def finalizar_dia(controle_id):
    try:
        data = request.form
        controle = ControleDiario.query.get_or_404(controle_id)
        
        # Converter valores para o tipo correto
        controle.km_final = int(data['km_final'])
        controle.combustivel_litros = float(data.get('combustivel_litros', 0) or 0)
        controle.valor_combustivel = float(data.get('valor_combustivel', 0) or 0)
        controle.observacoes = data.get('observacoes', '')
        
        db.session.commit()
        return jsonify({'status': 'success', 'message': 'Dia finalizado com sucesso!'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 400

@app.route('/despesa', methods=['POST'])
def adicionar_despesa():
    try:
        data = request.form
        despesa = Despesa(
            data=datetime.now().date(),  # Usa a data atual
            tipo=data['tipo'],
            descricao=data['descricao'],
            valor=float(data['valor']),
            veiculo_id=data.get('veiculo_id') if data.get('veiculo_id') else None,
            cliente=data.get('cliente'),
            reembolsavel=bool(data.get('reembolsavel', False))
        )
        db.session.add(despesa)
        db.session.commit()
        return jsonify({'status': 'success', 'message': 'Despesa adicionada com sucesso!'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 400

@app.route('/continuar-dia')
def continuar_dia():
    # Buscar controle do dia atual não finalizado
    controle = ControleDiario.query.filter_by(
        data=datetime.now().date(),
        km_final=None
    ).first()
    
    if controle:
        return redirect(url_for('movimentos', controle_id=controle.id))
    else:
        return redirect(url_for('iniciar_dia'))

@app.route('/relatorios')
def relatorios():
    # Buscar dados para o relatório
    data_inicial = request.args.get('data_inicial', datetime.now().date().replace(day=1))
    data_final = request.args.get('data_final', datetime.now().date())
    veiculo_id = request.args.get('veiculo')
    periodo = request.args.get('periodo', 'mes')

    # Filtrar dados
    query = db.session.query(
        Movimento.data,
        db.func.sum(Movimento.valor).label('receitas'),
        db.func.count(Movimento.id).label('qtd_servicos')
    ).group_by(Movimento.data)

    if veiculo_id:
        query = query.join(ControleDiario).filter(ControleDiario.veiculo_id == veiculo_id)

    movimentos = query.all()

    # Calcular resumo
    resumo = {
        'receitas': sum(m.receitas for m in movimentos),
        'despesas': Despesa.query.filter(
            Despesa.data.between(data_inicial, data_final)
        ).with_entities(db.func.sum(Despesa.valor)).scalar() or 0,
        'km_total': ControleDiario.query.filter(
            ControleDiario.data.between(data_inicial, data_final)
        ).with_entities(
            db.func.sum(ControleDiario.km_final - ControleDiario.km_inicial)
        ).scalar() or 0
    }
    resumo['resultado'] = resumo['receitas'] - resumo['despesas']

    veiculos = Veiculo.query.all()

    return render_template('relatorios.html', 
                         resumo=resumo, 
                         veiculos=veiculos,
                         movimentos=movimentos)

@app.route('/api/relatorios/dados')
def dados_relatorios():
    data_inicial = datetime.strptime(request.args.get('data_inicial'), '%Y-%m-%d').date()
    data_final = datetime.strptime(request.args.get('data_final'), '%Y-%m-%d').date()
    veiculo_id = request.args.get('veiculo')
    periodo = request.args.get('periodo', 'mes')

    # Query base para movimentos
    query_movimentos = Movimento.query.join(ControleDiario).filter(
        Movimento.data.between(data_inicial, data_final)
    )

    # Query base para despesas
    query_despesas = Despesa.query.filter(
        Despesa.data.between(data_inicial, data_final)
    )

    if veiculo_id:
        query_movimentos = query_movimentos.filter(ControleDiario.veiculo_id == veiculo_id)
        query_despesas = query_despesas.filter(Despesa.veiculo_id == veiculo_id)

    # Dados para gráficos
    receitas_diarias = db.session.query(
        Movimento.data,
        db.func.sum(Movimento.valor).label('valor')
    ).group_by(Movimento.data).all()

    despesas_diarias = db.session.query(
        Despesa.data,
        db.func.sum(Despesa.valor).label('valor')
    ).group_by(Despesa.data).all()

    formas_pagamento = db.session.query(
        Movimento.forma_pagamento,
        db.func.sum(Movimento.valor).label('valor')
    ).group_by(Movimento.forma_pagamento).all()

    # Dados para tabelas
    movimentos = [{
        'data': m.data,
        'cliente': m.cliente,
        'tipo_servico': m.tipo_servico,
        'valor': m.valor,
        'forma_pagamento': m.forma_pagamento
    } for m in query_movimentos.all()]

    despesas = [{
        'data': d.data,
        'tipo': d.tipo,
        'descricao': d.descricao,
        'valor': d.valor,
        'veiculo': d.veiculo.placa if d.veiculo_id else None
    } for d in query_despesas.all()]

    # Análise por veículo
    veiculos = []
    for veiculo in Veiculo.query.all():
        controles = ControleDiario.query.filter(
            ControleDiario.veiculo_id == veiculo.id,
            ControleDiario.data.between(data_inicial, data_final)
        ).all()
        
        km_total = sum(c.km_final - c.km_inicial for c in controles if c.km_final)
        total_combustivel = sum(c.combustivel_litros or 0 for c in controles)
        total_despesas = sum(d.valor for d in despesas if d.veiculo_id == veiculo.id)
        
        veiculos.append({
            'placa': veiculo.placa,
            'km_total': km_total,
            'consumo_medio': km_total / total_combustivel if total_combustivel else 0,
            'custo_km': total_despesas / km_total if km_total else 0,
            'total_despesas': total_despesas
        })

    return jsonify({
        'receitas': [{'data': r.data, 'valor': float(r.valor)} for r in receitas_diarias],
        'despesas': [{'data': d.data, 'valor': float(d.valor)} for d in despesas_diarias],
        'pagamentos': [{'forma': p.forma_pagamento, 'valor': float(p.valor)} for p in formas_pagamento],
        'movimentos': movimentos,
        'despesas': despesas,
        'veiculos': veiculos
    })

@app.route('/api/relatorios/export')
def exportar_relatorio():
    # Implementar exportação para Excel
    pass

@app.route('/movimento/<int:id>', methods=['PUT', 'DELETE'])
def gerenciar_movimento(id):
    movimento = Movimento.query.get_or_404(id)
    
    if request.method == 'PUT':
        data = request.json
        movimento.cliente = data.get('cliente', movimento.cliente)
        movimento.tipo_servico = data.get('tipo_servico', movimento.tipo_servico)
        movimento.descricao = data.get('descricao', movimento.descricao)
        movimento.valor = data.get('valor', movimento.valor)
        movimento.forma_pagamento = data.get('forma_pagamento', movimento.forma_pagamento)
        db.session.commit()
        return jsonify({'status': 'success'})
    
    elif request.method == 'DELETE':
        db.session.delete(movimento)
        db.session.commit()
        return jsonify({'status': 'success'})

def init_database():
    with app.app_context():
        # Criar todas as tabelas
        db.create_all()
        
        # Adicionar veículo inicial (exemplo)
        if not Veiculo.query.first():
            veiculo = Veiculo(placa='ABC-1234', modelo='Fiorino')
            db.session.add(veiculo)
            db.session.commit()

if __name__ == '__main__':
    init_database()
    print("Banco de dados inicializado com sucesso!")
    app.run(debug=True) 