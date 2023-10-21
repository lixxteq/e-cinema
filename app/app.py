from flask import Flask
from flask_migrate import Migrate
from dotenv import load_dotenv
from os import getenv

from models import db

application = app = Flask(__name__)
load_dotenv()
app.config.from_object('config.DevConfig' if getenv('FLASK_ENV') == 'development' else 'config.ProdConfig')

db.init_app(app)
migrate = Migrate(app, db)
with app.app_context():
    db.create_all()