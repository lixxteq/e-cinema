from os import getenv, path
from dotenv import load_dotenv
load_dotenv()

class Config(object):
    SECRET_KEY = getenv('SECRET_KEY', 'not_a_secret')
    JWT_SECRET_KEY = SECRET_KEY
    DB_NAME = 'ecdb'
    BASE_URL = 'mysql+mysqldb://%s:%s@%s:3306/%s?charset=utf8&auth_plugin=mysql_native_password'
    SQLALCHEMY_DATABASE_URI = BASE_URL % (getenv('MYSQL_USER'), getenv('MYSQL_PASSWORD'), getenv('MYSQL_HOST'), DB_NAME)
    ENGINE_URI = BASE_URL % (getenv('MYSQL_USER'), getenv('MYSQL_PASSWORD'), getenv('MYSQL_HOST'), '')
    UPLOAD_FOLDER = path.join(path.dirname(path.abspath(__file__)), 'upload')
    APP_PORT = getenv('APP_PORT', 39015)
    SERVICE_PORT = getenv('SERVICE_PORT', 39016)
    JWT_TOKEN_LOCATION = ['cookies']

class DevConfig(Config):
    DEBUG = True
    ENV = 'development'
    SQLALCHEMY_ECHO = True
    SQLALCHEMY_TRACK_MODIFICATIONS = True
    TEMPLATES_AUTO_RELOAD = True
    DEBUG_TB_INTERCEPT_REDIRECTS = False
    SERVICE_HOST = 'http://0.0.0.0:%s'
    SERVICE_URI = SERVICE_HOST % Config.SERVICE_PORT
    JWT_COOKIE_SECURE = False

class ProdConfig(Config):
    DEBUG = False
    SERVICE_HOST = 'http://hls_service:%s'
    SERVICE_URI = SERVICE_HOST % Config.SERVICE_PORT
    JWT_COOKIE_SECURE = True