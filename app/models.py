from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from app import db, login_manager
from datetime import datetime

@login_manager.user_loader
def load_user(id):
    return User.query.get(int(id))

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    is_admin = db.Column(db.Boolean, default=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Veiculo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    placa = db.Column(db.String(8), unique=True, nullable=False)
    modelo = db.Column(db.String(50))
    status = db.Column(db.String(20), default='Ativo')
    controles = db.relationship('ControleDiario', backref='veiculo', lazy=True)
    despesas = db.relationship('Despesa', backref='veiculo', lazy=True)

class ControleDiario(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    data = db.Column(db.Date, nullable=False)
    veiculo_id = db.Column(db.Integer, db.ForeignKey('veiculo.id'), nullable=False)
    km_inicial = db.Column(db.Integer)
    km_final = db.Column(db.Integer)
    combustivel_litros = db.Column(db.Float)
    valor_combustivel = db.Column(db.Float)
    observacoes = db.Column(db.Text)
    movimentos = db.relationship('Movimento', backref='controle', lazy=True)

class Movimento(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    data = db.Column(db.Date, nullable=False)
    controle_id = db.Column(db.Integer, db.ForeignKey('controle_diario.id'))
    cliente = db.Column(db.String(100), nullable=False)
    tipo_servico = db.Column(db.String(50))
    descricao = db.Column(db.Text)
    valor = db.Column(db.Float, nullable=False)
    forma_pagamento = db.Column(db.String(20))
    status_pagamento = db.Column(db.String(20), default='Pendente')
    data_pagamento = db.Column(db.Date)

class Despesa(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    data = db.Column(db.Date, nullable=False)
    tipo = db.Column(db.String(50))
    descricao = db.Column(db.Text)
    valor = db.Column(db.Float, nullable=False)
    veiculo_id = db.Column(db.Integer, db.ForeignKey('veiculo.id'), nullable=True)
    cliente = db.Column(db.String(100))
    reembolsavel = db.Column(db.Boolean, default=False)
    status_reembolso = db.Column(db.String(20)) 