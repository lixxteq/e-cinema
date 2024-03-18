from crypt import methods
from ..forms import LoginForm, RegisterForm
from ..models import Role, db, User
from flask import Blueprint, render_template, redirect, url_for, request
from flask_login import LoginManager, login_user, logout_user, login_required
from sqlalchemy import select, insert
from ..utils import access_guard, flash_alert, flash_errors, seq_fetch_one
from flask_bcrypt import generate_password_hash
from ..app import current_user

controller = Blueprint('auth', __name__, url_prefix='/auth')

def load_user(user_id):
    return db.session.scalar(select(User).where(User.id == user_id))

def create_login_manager(app):
    login_manager = LoginManager()
    login_manager.login_view = 'auth.login' # type: ignore
    login_manager.login_message = 'Пройдите аутентификацию для доступа к странице.'
    login_manager.login_message_category = 'warning'
    login_manager.user_loader(load_user)
    login_manager.init_app(app)

@controller.route('login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if request.method == 'POST':
        # if form.validate_on_submit():
            user = db.session.scalar(select(User).where((User.login == form.login.data)|(User.email == form.login.data)))
            if user and user.check_password(form.password.data):
                login_user(user, remember=form.remember_me.data)
                flash_alert(f'Logged in as {user.display_name}', 'success')
                return redirect(request.args.get('next') or url_for('index'))
            else: flash_alert('Incorrect login or password', 'danger')
    return render_template('auth/login.html', form=form)

@controller.route('logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@controller.route('register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    if request.method == 'POST':
        if not form.validate_on_submit() or not form.password.data == form.repeat_password.data:
            flash_errors(form)
            return redirect(url_for('auth.register'))
        # TODO: email validation
        user = User(login = form.login.data, display_name = form.display_name.data, email = form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash_alert('Регистрация пройдена', 'success')
        return redirect(url_for('index'))
    return render_template('auth/register.html', form=form)

# developer mode only
@controller.route('devrg')
# @access_guard(current_user, 'administrator')
def devrg():
    roles = db.session.scalars(select(Role)).all()
    user1 = User(
        login = 'visitor1',
        password_hash = generate_password_hash('visitor1').decode(),
        email = 'qwerty1@domain.com',
        display_name = 'display1',
        role = seq_fetch_one(roles, 'name', 'visitor'),
        # role = [x for x in roles if x.name == 'visitor'][0]
        # role_id = 1
    )
    user2 = User(
        login = 'moderator1',
        password_hash = generate_password_hash('moderator1').decode(),
        email = 'qwerty2@domain.com',
        display_name = 'display2',
        # role = next(filter(lambda x: x.name == 'moderator', roles)),
        role = seq_fetch_one(roles, 'name', 'moderator')
        # role = [x for x in roles if x.name == 'moderator'][0]
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
        # role = [x for x in roles if x.name == 'administrator'][0]
        # role_id = 3d
    )

    db.session.add_all([user1, user2, user3])
    db.session.commit()
    return redirect(url_for('auth.login'))