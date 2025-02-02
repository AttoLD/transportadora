from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from flask_login import login_user, logout_user, login_required, current_user
from app.models import User
from app import db

bp = Blueprint('auth', __name__)

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

@bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.index')) 