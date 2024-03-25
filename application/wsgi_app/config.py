from os import getenv, path
from pathlib import Path
from dotenv import load_dotenv

from application.shared import SharedConfig
load_dotenv()

class Config(SharedConfig):
    SECRET_KEY = getenv('SECRET_KEY', 'not_a_secret')
    JWT_SECRET_KEY = SECRET_KEY
    DB_NAME = 'ecdb'
    BASE_URL = 'mysql+mysqldb://%s:%s@%s:3306/%s?charset=utf8&auth_plugin=mysql_native_password'
    SQLALCHEMY_DATABASE_URI = BASE_URL % (getenv('MYSQL_USER'), getenv('MYSQL_PASSWORD'), getenv('MYSQL_HOST'), DB_NAME)
    ENGINE_URI = BASE_URL % (getenv('MYSQL_USER'), getenv('MYSQL_PASSWORD'), getenv('MYSQL_HOST'), '')
    # UPLOAD_FOLDER = path.join(path.dirname(path.abspath(__file__)), 'upload')
    UPLOAD_DIR = str(Path(__file__).parents[2] / 'upload')
    APP_PORT = int(getenv('APP_PORT', 39015))
    SERVICE_PORT = int(getenv('SERVICE_PORT', 39016))
    JWT_TOKEN_LOCATION = ['cookies']
    JWT_ALGORITHM = 'HS256'
    BEFORE_REQUEST_OMIT = ('auth.login')
    ACCESS_TOKEN_EXPIRE_HOURS = 24 # no impl
    JWT_COOKIE_DOMAIN = 'localhost' # should be configured to same-domain

class DevConfig(Config):
    DEBUG = True
    ENV = 'development'
    SQLALCHEMY_ECHO = True
    SQLALCHEMY_TRACK_MODIFICATIONS = True
    TEMPLATES_AUTO_RELOAD = True
    DEBUG_TB_INTERCEPT_REDIRECTS = False
    # SERVICE_HOST = 'http://0.0.0.0:%s'
    SERVICE_HOST = getenv('SERVICE_HOST', 'localhost')
    SERVICE_URI = f'{SERVICE_HOST}:{Config.SERVICE_PORT}'
    JWT_COOKIE_SECURE = False

class ProdConfig(Config):
    DEBUG = False
    SERVICE_HOST = 'http://hls_service:%s'
    SERVICE_URI = SERVICE_HOST % Config.SERVICE_PORT
    JWT_COOKIE_SECURE = True
