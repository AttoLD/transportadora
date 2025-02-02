from app import app, db
from models import Veiculo

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