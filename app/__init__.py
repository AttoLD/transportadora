from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from config import Config
from flask_talisman import Talisman
import logging
from logging.handlers import RotatingFileHandler
import os
from authlib.integrations.flask_client import OAuth

db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()
oauth = OAuth()
login_manager.login_view = 'auth.login'
login_manager.login_message = 'Por favor, faça login para acessar esta página.'

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    oauth.init_app(app)
    Talisman(app, force_https=True)

    from app.routes import main, movimentos, relatorios, auth
    app.register_blueprint(main.bp)
    app.register_blueprint(movimentos.bp, url_prefix='/movimentos')
    app.register_blueprint(relatorios.bp, url_prefix='/relatorios')
    app.register_blueprint(auth.bp, url_prefix='/auth')

    # Configuração de logs
    if not app.debug and not app.testing:
        if not os.path.exists('logs'):
            os.mkdir('logs')
        file_handler = RotatingFileHandler('logs/transportadora.log',
                                         maxBytes=10240, backupCount=10)
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s '
            '[in %(pathname)s:%(lineno)d]'
        ))
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)
        app.logger.setLevel(logging.INFO)
        app.logger.info('Transportadora startup')

    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        app.logger.error(f'Server Error: {error}')
        return render_template('errors/500.html'), 500

    @app.errorhandler(404)
    def not_found_error(error):
        return render_template('errors/404.html'), 404

    return app 