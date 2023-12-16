from flask import Flask, render_template, request
from flask_login import current_user, login_required # type: ignore
from dotenv import load_dotenv
from os import getenv
from db_factory import Database
from sqlalchemy import select, desc, func
from values import ACCESS_LEVEL_MAP, BOOKS_PER_PAGE
from flask_debugtoolbar import DebugToolbarExtension

load_dotenv()
application = app = Flask(__name__)
app.config.from_object('config.DevConfig' if getenv('FLASK_ENV') == 'development' else 'config.ProdConfig')
if app.config['ENV'] == 'development': 
    print(app.config)

db = Database(app=app)
migrate = db.init_migrate()
toolbar = DebugToolbarExtension(app=app)

from models import Book, User
from utils import flash_alert
from controllers.auth import controller as auth_bp, create_login_manager
from controllers.books import controller as books_bp
app.register_blueprint(auth_bp)
app.register_blueprint(books_bp)
create_login_manager(app)

# enforce User type to fix type recognition of current_user variable
current_user: User = current_user

@app.context_processor
def globals(): 
    return {
        'access_level_map': ACCESS_LEVEL_MAP
    }

@app.route('/')
def index():
    page = request.args.get('page', 1, type=int)
    pages = db.session.execute(select(func.count(Book.id))).scalar_one()
    books = db.session.scalars(select(Book).order_by(desc(Book.year)).limit(BOOKS_PER_PAGE).offset((page-1) * BOOKS_PER_PAGE)).all()
    return render_template('index.html', books=books, page=page, pages=pages)