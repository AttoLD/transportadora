from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from config import Config
from flask_talisman import Talisman

db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()
login_manager.login_view = 'auth.login'
login_manager.login_message = 'Por favor, faça login para acessar esta página.'

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    Talisman(app, force_https=True)

    from app.routes import main, movimentos, relatorios, auth
    app.register_blueprint(main.bp)
    app.register_blueprint(movimentos.bp, url_prefix='/movimentos')
    app.register_blueprint(relatorios.bp, url_prefix='/relatorios')
    app.register_blueprint(auth.bp, url_prefix='/auth')

    return app 