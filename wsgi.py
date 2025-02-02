from app import create_app, db
from app.models import User
import os
import logging

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = create_app()

# Criar as tabelas e usuário admin apenas em desenvolvimento
if not os.environ.get('RENDER'):
    with app.app_context():
        try:
            logger.info("Iniciando criação das tabelas...")
            db.create_all()
            
            if not User.query.filter_by(username='admin').first():
                logger.info("Criando usuário admin...")
                user = User(username='admin', is_admin=True)
                user.set_password('admin123')
                db.session.add(user)
                db.session.commit()
                logger.info("Usuário admin criado com sucesso")
        except Exception as e:
            logger.error(f"Erro durante a inicialização: {str(e)}")
            raise

if __name__ == "__main__":
    app.run() 