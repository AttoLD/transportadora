from app import create_app, db
from app.models import User

def create_admin_user():
    app = create_app()
    with app.app_context():
        if not User.query.filter_by(username='admin').first():
            user = User(username='admin', is_admin=True)
            user.set_password('sua-senha-aqui')
            db.session.add(user)
            db.session.commit()
            print('Usuário admin criado com sucesso!')

if __name__ == '__main__':
    create_admin_user() 