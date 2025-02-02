from app import create_app, db
from app.models import User

app = create_app()

# Criar as tabelas e usuário admin na primeira execução
with app.app_context():
    db.create_all()
    if not User.query.filter_by(username='admin').first():
        user = User(username='admin', is_admin=True)
        user.set_password('admin123')  # Mude esta senha!
        db.session.add(user)
        db.session.commit()

if __name__ == "__main__":
    app.run() 