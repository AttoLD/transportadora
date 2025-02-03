import os
from urllib.parse import urlparse
import logging
from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '.env'))

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'você-nunca-adivinhará'
    
    # Configuração do banco de dados
    try:
        if os.environ.get('RENDER') == 'true':
            # URL do banco PostgreSQL no Render
            database_url = os.environ.get('DATABASE_URL')
            if not database_url:
                raise ValueError("DATABASE_URL não está configurada")
            
            if database_url.startswith("postgres://"):
                database_url = database_url.replace("postgres://", "postgresql://", 1)
            
            # Configurações específicas para PostgreSQL
            SQLALCHEMY_ENGINE_OPTIONS = {
                'pool_size': 5,
                'max_overflow': 2,
                'pool_timeout': 30,
                'pool_recycle': 1800,
            }
        else:
            # SQLite local para desenvolvimento
            database_url = 'sqlite:///' + os.path.join(basedir, 'app.db')
        
        SQLALCHEMY_DATABASE_URI = database_url
        SQLALCHEMY_TRACK_MODIFICATIONS = False
        
    except Exception as e:
        logging.error(f"Erro na configuração do banco de dados: {str(e)}")
        raise 

    # Configurações do Google OAuth
    GOOGLE_CLIENT_ID = os.environ.get('GOOGLE_CLIENT_ID')
    GOOGLE_CLIENT_SECRET = os.environ.get('GOOGLE_CLIENT_SECRET') 