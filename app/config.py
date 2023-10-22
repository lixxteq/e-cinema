from os import getenv, path

class Config(object):
    SECRET_KEY = '018b681f-8947-7f04-8cc7-b2cf1ba230ef' # non-private
    SQLALCHEMY_DATABASE_URI = getenv('SQLALCHEMY_DATABASE_URI')
    UPLOAD_DIR = path.join(path.dirname(path.abspath(__file__)), 'upload')

class DevConfig(Config):
    DEBUG = True
    ENV = 'development'
    SQLALCHEMY_ECHO = True
    SQLALCHEMY_TRACK_MODIFICATIONS = True

class ProdConfig(Config):
    DEBUG = False