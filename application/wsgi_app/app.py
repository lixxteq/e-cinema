from flask import Flask, render_template, request
from flask_login import current_user, login_required # type: ignore
from dotenv import load_dotenv
from os import getenv
from sqlalchemy import select, desc, func
from values import ACCESS_LEVEL_MAP, MEDIA_PER_PAGE
from flask_debugtoolbar import DebugToolbarExtension
import pathlib
import sys

_parentdir = pathlib.Path(__file__).parent.parent.resolve()
sys.path.insert(0, str(_parentdir))
from db_factory import Database
sys.path.remove(str(_parentdir))

load_dotenv()
application = app = Flask(__name__)
app.config.from_object('config.DevConfig' if getenv('FLASK_ENV') == 'development' else 'config.ProdConfig')
if app.config['ENV'] == 'development': 
    print(app.config)

db = Database(app=app)
migrate = db.init_migrate()
toolbar = DebugToolbarExtension(app=app)

from models import Media, User
from utils import flash_alert
from controllers.auth import controller as auth_bp, create_login_manager
from controllers.title import controller as title_bp
from controllers.admin.index import controller as admin_bp
from controllers.watch import controller as watch_bp

app.register_blueprint(auth_bp)
app.register_blueprint(title_bp)
app.register_blueprint(admin_bp)
app.register_blueprint(watch_bp)
create_login_manager(app)

# enforce User type to fix type recognition of current_user variable
current_user: User = current_user

@app.context_processor
def globals(): 
    return {
        'access_level_map': ACCESS_LEVEL_MAP
    }

@app.errorhandler(404)
def http_not_found(error):
    return render_template('not_found.html')

@app.route('/')
def index():
    page = request.args.get('page', 1, type=int)
    pages = db.session.execute(select(func.count(Media.media_id))).scalar_one()
    media = db.session.scalars(select(Media).order_by(desc(Media.year)).limit(MEDIA_PER_PAGE).offset((page-1) * MEDIA_PER_PAGE)).all()
    return render_template('index.html', media=media, page=page, pages=pages)