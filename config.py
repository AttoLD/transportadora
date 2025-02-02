import os
from urllib.parse import urlparse

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'chave-secreta-padrao'
    
    # Configuração do banco de dados
    if os.environ.get('FLASK_ENV') == 'production':
        # URL do banco PostgreSQL no Render
        database_url = os.environ.get('DATABASE_URL', 'postgresql://transportadora_db_user:ZwqiPqzWIcZU5dwZUWLjQiEWbNVOdBgd@dpg-cuftrshopnds73b8vteg-a/transportadora_db')
        if database_url.startswith("postgres://"):
            database_url = database_url.replace("postgres://", "postgresql://", 1)
    else:
        # SQLite local para desenvolvimento
        basedir = os.path.abspath(os.path.dirname(__file__))
        database_url = 'sqlite:///' + os.path.join(basedir, 'instance', 'transportadora.db')
    
    SQLALCHEMY_DATABASE_URI = database_url
    SQLALCHEMY_TRACK_MODIFICATIONS = False 