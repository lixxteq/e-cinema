from os import getenv, path
from dotenv import load_dotenv
load_dotenv()

class Config(object):
    SECRET_KEY = '018b681f-8947-7f04-8cc7-b2cf1ba230ef' # non-private
    DB_NAME = 'ecdb'
    # SQLALCHEMY_DATABASE_URI = getenv('SQLALCHEMY_DATABASE_URI')
    BASE_URL = 'mysql+mysqldb://%s:%s@%s:3306/%s?charset=utf8&auth_plugin=mysql_native_password'
    SQLALCHEMY_DATABASE_URI = BASE_URL % (getenv('MYSQL_USER'), getenv('MYSQL_PASSWORD'), getenv('MYSQL_HOST'), DB_NAME)
    ENGINE_URI = BASE_URL % (getenv('MYSQL_USER'), getenv('MYSQL_PASSWORD'), getenv('MYSQL_HOST'), '')
    UPLOAD_FOLDER = path.join(path.dirname(path.abspath(__file__)), 'upload')
    POOL_WORKERS = 5

class DevConfig(Config):
    DEBUG = True
    ENV = 'development'
    SQLALCHEMY_ECHO = True
    SQLALCHEMY_TRACK_MODIFICATIONS = True
    TEMPLATES_AUTO_RELOAD = True
    DEBUG_TB_INTERCEPT_REDIRECTS = False
    SERVICE_HOST = 'http://127.0.0.1:%s'
    SERVICE_PORT = 39016
    SERVICE_URI = SERVICE_HOST % SERVICE_PORT

class ProdConfig(Config):
    DEBUG = False
    APP_PORT = 39015
    SERVICE_HOST = 'http://media_worker:%s'
    SERVICE_URI = SERVICE_HOST % APP_PORT