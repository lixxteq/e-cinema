from models import Role, db, User
from flask import Blueprint, render_template, redirect, url_for, request
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from sqlalchemy import select, insert
from utils import flash_alert
from flask_bcrypt import generate_password_hash

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
                flash_alert(f'Вы вошли как {user.login} ({user.first_name})', 'success')
                return redirect(request.args.get('next') or url_for('index'))
        flash_alert('Невозможно аутентифицироваться с указанными логином и паролем', 'danger')
    return render_template('login.html')

@controller.route('logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

# development only
@controller.route('create')
def create():
    roles = db.session.scalars(select(Role)).all()

    user1 = User(
        login = 'visitor',
        password_hash = generate_password_hash('12345').decode(),
        first_name = 'Ivan',
        last_name = 'Ivanov',
        middle_name = 'I',
        role = roles[0],
        # role_id = 1
    )
    user2 = User(
        login = 'moderator',
        password_hash = generate_password_hash('12345').decode(),
        first_name = 'Alexandr',
        last_name = 'Alexandrov',
        middle_name = 'A',
        role_id = roles[1],
        # role_id = 2
    )
    user3 = User(
        login = 'admin',
        password_hash = generate_password_hash('12345').decode(),
        first_name = 'R',
        last_name = 'Z',
        middle_name = 'D',
        role_id = roles[2],
        # role_id = 3
    )

    db.session.add_all([user1, user2, user3])
    db.session.commit()
    return redirect(url_for('auth.login'))