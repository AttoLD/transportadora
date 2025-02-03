from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app, session
from flask_login import login_user, logout_user, login_required, current_user
from app.models import User
from app import db, oauth
import os

bp = Blueprint('auth', __name__)

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
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()
        
        if user and user.check_password(password):
            login_user(user)
            next_page = request.args.get('next')
            return redirect(next_page or url_for('main.index'))
        
        flash('Usuário ou senha inválidos')
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
    if request.method == 'POST':
        firstname = request.form.get('firstname')
        lastname = request.form.get('lastname')
        email = request.form.get('email')
        password = request.form.get('password')
        
        if User.query.filter_by(email=email).first():
            flash('Email já cadastrado')
            return redirect(url_for('auth.register'))
        
        user = User(
            username=email,
            email=email,
            firstname=firstname,
            lastname=lastname
        )
        user.set_password(password)
        
        db.session.add(user)
        db.session.commit()
        
        login_user(user)
        return redirect(url_for('main.index'))
        
    return render_template('auth/register.html')

@bp.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    return render_template('auth/forgot_password.html')

@bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login')) 