from models import db, User
from flask import Blueprint, render_template, redirect, url_for, request
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from sqlalchemy import select
from utils import flash_alert

controller = Blueprint('auth', __name__, url_prefix='/auth')

def load_user(user_id):
    return User.query.get(user_id)

def create_login_manager(app):
    login_manager = LoginManager()
    login_manager.login_view = 'auth.login' # type: ignore
    login_manager.login_message = 'Пройдите аутентификацию для доступа к странице.'
    login_manager.login_message_category = 'warning'
    login_manager.user_loader(load_user)
    login_manager.init_app(app)

def role_access():
    return True

@controller.route('login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        login = request.form.get('login')
        password = request.form.get('password')
        if login and password:
            user = db.session.execute(select(User).filter_by(login=login)).scalar()
            if user and user.check_password(password):
                login_user(user)
                flash_alert(f'Вы вошли как {user.login} ({user.first_name})', 'success')
                return redirect(request.args.get('next') or url_for('index'))
        flash_alert('Невозможно аутентифицироваться с указанными логином и паролем', 'error')
    return render_template('login.html')

@controller.route('logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))