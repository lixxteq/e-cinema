from flask import Flask
from flask_debugtoolbar import DebugToolbarExtension
from flask_migrate import Migrate
from dotenv import load_dotenv
from os import getenv
from db_factory import database_factory

application = app = Flask(__name__)
load_dotenv()
app.config.from_object('config.DevConfig' if getenv('FLASK_ENV') == 'development' else 'config.ProdConfig')

debugtb = DebugToolbarExtension(app)
db = database_factory(app)
migrate = Migrate(app, db)

