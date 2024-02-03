from models import Role, db, User
from flask import Blueprint, render_template, redirect, url_for, request
from flask_login import LoginManager, login_user, logout_user, login_required
from sqlalchemy import select, insert
from utils import flash_alert, seq_fetch_one
from flask_bcrypt import generate_password_hash
from app import current_user

controller = Blueprint('auth', __name__, url_prefix='/auth')

def load_user(user_id):
    return db.session.scalar(select(User).where(User.id == user_id))
    # return User.query.get(user_id)

def create_login_manager(app):
    login_manager = LoginManager()
    login_manager.login_view = 'auth.login' # type: ignore
    login_manager.login_message = 'Пройдите аутентификацию для доступа к странице.'
    login_manager.login_message_category = 'warning'
    login_manager.user_loader(load_user)
    login_manager.init_app(app)
    

@controller.route('login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        login = request.form.get('login')
        password = request.form.get('password')
        remember_me = request.form.get('remember_me', type=bool)
        if login and password:
            user = db.session.scalar(select(User).filter_by(login=login))
            if user and user.check_password(password):
                login_user(user, remember=bool(remember_me))
                flash_alert(f'Вы вошли как {user.login}', 'success')
                return redirect(request.args.get('next') or url_for('index'))
        flash_alert('Невозможно аутентифицироваться с указанными логином и паролем', 'danger')
    return render_template('auth/login.html')

@controller.route('logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@controller.route('register')
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    if request.method == 'POST':
        login = request.form.get('login')
        password = request.form.get('password')
        password_confirm = request.form.get('confirm_password')
        email = request.form.get('email')
        if login and password and email and password == password_confirm:
            user = User(login = login, )
            user.set_password(password)
    return render_template('register.html')

# developer mode only
@controller.route('devrg')
def devrg():
    roles = db.session.scalars(select(Role)).all()
    user1 = User(
        login = 'visitor1',
        password_hash = generate_password_hash('visitor1').decode(),
        email = 'qwerty1@domain.com',
        display_name = 'display1',
        role = seq_fetch_one(roles, 'name', 'visitor'),
        # role_id = 1
    )
    user2 = User(
        login = 'moderator1',
        password_hash = generate_password_hash('moderator1').decode(),
        email = 'qwerty2@domain.com',
        display_name = 'display2',
        # role = next(filter(lambda x: x.name == 'moderator', roles)),
        role = seq_fetch_one(roles, 'name', 'moderator')
        # roles.
        # role_id = 2
    )
    user3 = User(
        login = 'administrator1',
        password_hash = generate_password_hash('administrator1').decode(),
        email = 'qwerty3@domain.com',
        display_name = 'display3',
        # role = next(filter(lambda x: x.name == 'administrator', rdict)),
        role = seq_fetch_one(roles, 'name', 'administrator')
        # role_id = 3d
    )

    db.session.add_all([user1, user2, user3])
    db.session.commit()
    return redirect(url_for('auth.login'))

# @controller.route('create')
# @login_required
# def create():
#     return render_template()