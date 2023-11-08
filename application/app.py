from flask import Flask, render_template, request
from flask_login import current_user, login_required
from dotenv import load_dotenv
from os import getenv
from db_factory import Database
from sqlalchemy import select, desc, func
from values import BOOKS_PER_PAGE, ADMIN_ACCESS_LEVEL, VISITOR_ACCESS_LEVEL, MODERATOR_ACCESS_LEVEL

load_dotenv()
application = app = Flask(__name__)
app.config.from_object('config.DevConfig' if getenv('FLASK_ENV') == 'development' else 'config.ProdConfig')

db = Database(app=app)
migrate = db.init_migrate()

from models import Book
from utils import flash_alert, get_access_level, is_anonimous
from controllers.auth import controller as auth_bp, create_login_manager
from controllers.books import controller as books_bp, has_access
app.register_blueprint(auth_bp)
app.register_blueprint(books_bp)
create_login_manager(app)

@app.context_processor
def check_user_status(): 
    return dict(is_anon=is_anonimous())

@app.route('/')
def index():
    page = request.args.get('page', 1, type=int)
    pages = db.session.execute(select(func.count(Book.id))).scalar_one()
    books = db.session.scalars(select(Book).order_by(desc(Book.year)).limit(BOOKS_PER_PAGE).offset((page-1) * BOOKS_PER_PAGE)).all()

    return render_template('index.html', books=books, page=page, pages=pages, access_level=get_access_level())