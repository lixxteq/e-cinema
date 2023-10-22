from flask import Flask, render_template, request
from flask_migrate import Migrate
from dotenv import load_dotenv
from os import getenv
from utils import flash_alert
from models import db

application = app = Flask(__name__)
load_dotenv()
app.config.from_object('config.DevConfig' if getenv('FLASK_ENV') == 'development' else 'config.ProdConfig')

db.init_app(app)
migrate = Migrate(app, db)
with app.app_context():
    db.create_all()

from controllers.auth import controller as auth_bp, create_login_manager
from controllers.books import controller as books_bp
app.register_blueprint(auth_bp)
app.register_blueprint(books_bp)
create_login_manager(app)

@app.route('/')
def index():
    flash_alert('asdfghgfasdf ghgfasdfghgfasd fghgfasd fghgfas dfghgfasdfghgfasdfghg fasdfghgfasdfghgfa sdfghgfasdfghg fasdfghgf', 'success')
    return render_template('index.html')