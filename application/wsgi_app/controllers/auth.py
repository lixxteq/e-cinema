from typing import Any
from ..forms import LoginForm, RegisterForm
from ...models import Role, User
from flask import Blueprint, g, make_response, render_template, redirect, url_for, request
# from flask_login import LoginManager, login_user, logout_user, jwt_required
from sqlalchemy import select, insert
from ..utils import access_guard, flash_alert, flash_errors, seq_fetch_one
from ..types import AnonymousUser
from flask_bcrypt import generate_password_hash
from ..app import app, db
import flask_jwt_extended as rewrite
from flask_jwt_extended import JWTManager, create_access_token, current_user, jwt_required, set_access_cookies, unset_jwt_cookies

def _get_current_user() -> User | None:
    jwt_user_dict = g.get("_jwt_extended_jwt_user", None)
    return jwt_user_dict["loaded_user"] if jwt_user_dict else None
rewrite.utils.get_current_user = _get_current_user

# enforce User type on user proxy for type hinting
current_user: User = current_user

jwtm = JWTManager(app, add_context_processor=True)

@jwtm.user_identity_loader
def user_identity_handler(user: User):
    return user.id.__str__()

@jwtm.user_lookup_loader
def user_lookup_handler(jwt_header, jwt_data):
    identity = jwt_data["sub"]
    t = db.session.scalars(select(User).where(User.id == identity)).one_or_none()
    print(t)
    return t

controller = Blueprint('auth', __name__, url_prefix='/auth')

@controller.route('login', methods=['GET', 'POST'])
def login():
    if current_user:
        return redirect(url_for('index'))
    form = LoginForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            user = db.session.scalar(select(User).where((User.login == form.login.data)|(User.email == form.login.data)))
            if user and user.check_password(form.password.data):
                resp = make_response(redirect(request.args.get('next') or url_for('index')))
                access_token = create_access_token(identity=user)
                set_access_cookies(response=resp, encoded_access_token=access_token)
                flash_alert(f'Logged in as {user.display_name}', 'success')
                return resp
        flash_alert('Incorrect login or password', 'danger')
    return render_template('auth/login.html', form=form)

@controller.route('logout')
def logout():
    resp = make_response(redirect(url_for('index')))
    unset_jwt_cookies(resp)
    # TODO: clear context?
    return resp

@controller.route('register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if current_user:
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