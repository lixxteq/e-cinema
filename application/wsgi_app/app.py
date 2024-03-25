

from flask import Flask, g, redirect, render_template, request, session, url_for
from flask_jwt_extended import jwt_required, verify_jwt_in_request
from flask_login import current_user, login_required # type: ignore
from dotenv import load_dotenv
from os import getenv
from sqlalchemy import select, desc, func, text
from .values import ACCESS_LEVEL_MAP, MEDIA_PER_PAGE
from flask_debugtoolbar import DebugToolbarExtension
from .config import DevConfig, ProdConfig
import pathlib

# _parentdir = pathlib.Path(__file__).parent.parent.resolve()
# sys.path.insert(0, str(_parentdir))
from ..db_factory import FlaskDatabase
# sys.path.remove(str(_parentdir))

load_dotenv()
app = Flask(__name__)
# application = WsgiToAsgi(wsgi_application=app)
# app = application.wsgi_application
# app = application.wsgi_application
app.config.from_object(DevConfig if getenv('FLASK_ENV') == 'development' else ProdConfig)
if app.config['ENV'] == 'development': 
    print(app.config)

db = FlaskDatabase(app=app)
migrate = db.init_migrate()
toolbar = DebugToolbarExtension(app=app)

from ..models import Media, User
db.init_schema()

from .utils import flash_alert
from .controllers.auth import controller as auth_bp
from .controllers.title import controller as title_bp
from .controllers.admin.index import controller as admin_bp
from .controllers.watch import controller as watch_bp

app.register_blueprint(auth_bp)
app.register_blueprint(title_bp)
app.register_blueprint(admin_bp)
app.register_blueprint(watch_bp)

@app.context_processor
def globals(): 
    return {
        'access_level_map': ACCESS_LEVEL_MAP
    }

@app.errorhandler(404)
def http_not_found(error):
    return render_template('not_found.html')

@app.errorhandler(401)
def unauthorized(error):
    flash_alert('Your authentication has expired, please log in again', 'danger')
    return redirect(url_for('auth.login'))

@app.before_request
def before_h():
    verify_jwt_in_request(optional=True)

@app.route('/')
# @jwt_required(optional=True)
def index():
    page = request.args.get('page', 1, type=int)
    pages = db.session.execute(select(func.count(Media.media_id))).scalar_one()
    media = db.session.scalars(select(Media).order_by(desc(Media.year)).limit(MEDIA_PER_PAGE).offset((page-1) * MEDIA_PER_PAGE)).all()
    return render_template('index.html', media=media, page=page, pages=pages)