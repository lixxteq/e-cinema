from os import getenv, path

class Config(object):
    SECRET_KEY = '018b681f-8947-7f04-8cc7-b2cf1ba230ef' # non-private
    DB_NAME = 'elib'
    # SQLALCHEMY_DATABASE_URI = getenv('SQLALCHEMY_DATABASE_URI')
    BASE_URL = 'mysql+mysqlconnector://root:admin@localhost/{0}?charset=utf8&auth_plugin=mysql_native_password'
    SQLALCHEMY_DATABASE_URI = BASE_URL.format(DB_NAME)
    RAW_SQLALCHEMY_DATABASE_URI = BASE_URL.format('')
    UPLOAD_FOLDER = path.join(path.dirname(path.abspath(__file__)), 'upload')


class DevConfig(Config):
    DEBUG = True
    ENV = 'development'
    SQLALCHEMY_ECHO = True
    SQLALCHEMY_TRACK_MODIFICATIONS = True
    TEMPLATES_AUTO_RELOAD = True

class ProdConfig(Config):
    DEBUG = False