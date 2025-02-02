from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class Veiculo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    placa = db.Column(db.String(8), unique=True, nullable=False)
    modelo = db.Column(db.String(50))
    status = db.Column(db.String(20), default='Ativo')

class ControleDiario(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    data = db.Column(db.Date, nullable=False)
    veiculo_id = db.Column(db.Integer, db.ForeignKey('veiculo.id'), nullable=False)
    km_inicial = db.Column(db.Integer)
    km_final = db.Column(db.Integer)
    combustivel_litros = db.Column(db.Float)
    valor_combustivel = db.Column(db.Float)
    observacoes = db.Column(db.Text)
    
    veiculo = db.relationship('Veiculo', backref='controles')

class Movimento(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    data = db.Column(db.Date, nullable=False)
    controle_id = db.Column(db.Integer, db.ForeignKey('controle_diario.id'))
    cliente = db.Column(db.String(100), nullable=False)
    tipo_servico = db.Column(db.String(50))  # Normal, Especial
    descricao = db.Column(db.Text)  # Descrição do serviço/carga
    valor = db.Column(db.Float, nullable=False)
    forma_pagamento = db.Column(db.String(20))
    status_pagamento = db.Column(db.String(20), default='Pendente')
    data_pagamento = db.Column(db.Date)

class Despesa(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    data = db.Column(db.Date, nullable=False)
    tipo = db.Column(db.String(50))  # Combustível, Manutenção, Cliente, Outros
    descricao = db.Column(db.Text)
    valor = db.Column(db.Float, nullable=False)
    veiculo_id = db.Column(db.Integer, db.ForeignKey('veiculo.id'), nullable=True)
    cliente = db.Column(db.String(100))  # Para despesas que serão reembolsadas
    reembolsavel = db.Column(db.Boolean, default=False)
    status_reembolso = db.Column(db.String(20)) 