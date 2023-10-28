from flask import Flask, render_template, request
from flask_login import current_user, login_required, AnonymousUserMixin
from flask_migrate import Migrate
from dotenv import load_dotenv
from os import getenv

from sqlalchemy import select, desc, func
from utils import flash_alert
from models import db, Book
from values import BOOKS_PER_PAGE, ADMIN_ACCESS_LEVEL, VISITOR_ACCESS_LEVEL, MODERATOR_ACCESS_LEVEL

application = app = Flask(__name__)
load_dotenv()
app.config.from_object('config.DevConfig' if getenv('FLASK_ENV') == 'development' else 'config.ProdConfig')
app.jinja_env.auto_reload = True

db.init_app(app)
migrate = Migrate(app, db)
with app.app_context():
    db.create_all()

from controllers.auth import controller as auth_bp, create_login_manager
from controllers.books import controller as books_bp, has_access
app.register_blueprint(auth_bp)
app.register_blueprint(books_bp)
create_login_manager(app)

@app.route('/')
def index():
    page = request.args.get('page', 1, type=int)
    pages = db.session.execute(select(func.count(Book.id))).scalar_one()
    books = db.session.scalars(select(Book).order_by(desc(Book.year)).limit(BOOKS_PER_PAGE).offset((page-1) * BOOKS_PER_PAGE)).all()
    # Проверка анонимности текущего пользователя через принадлежность к UserMixin классу анонимного пользователя
    if (isinstance(current_user._get_current_object(), AnonymousUserMixin)):
        access_level = VISITOR_ACCESS_LEVEL
    else: access_level = current_user._get_current_object().role_id

    return render_template('index.html', books=books, page=page, pages=pages, access_level=access_level)