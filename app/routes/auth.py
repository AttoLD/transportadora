from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app, session
from flask_login import login_user, logout_user, login_required, current_user
from app.models import User
from app import db
from authlib.integrations.flask_client import OAuth
import os

bp = Blueprint('auth', __name__)
oauth = OAuth()

# Configuração do Google OAuth
google = oauth.register(
    name='google',
    client_id=os.getenv('GOOGLE_CLIENT_ID'),
    client_secret=os.getenv('GOOGLE_CLIENT_SECRET'),
    access_token_url='https://accounts.google.com/o/oauth2/token',
    access_token_params=None,
    authorize_url='https://accounts.google.com/o/oauth2/auth',
    authorize_params=None,
    api_base_url='https://www.googleapis.com/oauth2/v1/',
    client_kwargs={'scope': 'openid email profile'},
)

@bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
        
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()
        
        try:
            if user is None or not user.check_password(password):
                current_app.logger.info(f'Falha no login para usuário: {username}')
                flash('Usuário ou senha inválidos')
                return redirect(url_for('auth.login'))
            
            login_user(user)
            current_app.logger.info(f'Login bem sucedido para usuário: {username}')
            next_page = request.args.get('next')
            if not next_page or not next_page.startswith('/'):
                next_page = url_for('main.index')
            return redirect(next_page)
            
        except Exception as e:
            current_app.logger.error(f'Erro no login: {str(e)}')
            db.session.rollback()
            flash('Ocorreu um erro. Por favor, tente novamente.')
            return redirect(url_for('auth.login'))
    
    return render_template('auth/login.html')

@bp.route('/google-login')
def google_login():
    redirect_uri = url_for('auth.google_authorize', _external=True)
    return google.authorize_redirect(redirect_uri)

@bp.route('/google-authorize')
def google_authorize():
    try:
        token = google.authorize_access_token()
        resp = google.get('userinfo')
        user_info = resp.json()
        email = user_info['email']
        
        user = User.query.filter_by(username=email).first()
        if not user:
            user = User(username=email)
            user.set_password(os.urandom(24).hex())
            db.session.add(user)
            db.session.commit()
        
        login_user(user)
        return redirect(url_for('main.index'))
    except Exception as e:
        current_app.logger.error(f'Erro no login com Google: {str(e)}')
        flash('Erro ao fazer login com Google')
        return redirect(url_for('auth.login'))

@bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
        
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if User.query.filter_by(username=username).first():
            flash('Este usuário já existe')
            return redirect(url_for('auth.register'))
            
        user = User(username=username)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        
        flash('Cadastro realizado com sucesso!')
        return redirect(url_for('auth.login'))
        
    return render_template('auth/register.html')

@bp.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    return render_template('auth/forgot_password.html')

@bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.index')) 