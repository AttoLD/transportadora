import os
from urllib.parse import urlparse

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'chave-secreta-padrao'
    
    # Ajuste para PostgreSQL no Render
    database_url = os.environ.get('postgresql://transportadora_db_user:ZwqiPqzWIcZU5dwZUWLjQiEWbNVOdBgd@dpg-cuftrshopnds73b8vteg-a/transportadora_db')
    if database_url:
        if database_url.startswith("postgres://"):
            database_url = database_url.replace("postgres://", "postgresql://", 1)
    else:
        database_url = 'sqlite:///transportadora.db'
    
    SQLALCHEMY_DATABASE_URI = database_url
    SQLALCHEMY_TRACK_MODIFICATIONS = False 