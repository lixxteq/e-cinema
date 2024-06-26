import os
from pydantic_settings import BaseSettings, SettingsConfigDict
from pathlib import Path
from application.shared import SharedConfig


class Config(BaseSettings):
    SECRET_KEY: str
    UPLOAD_DIR: str = str(Path(__file__).parents[2] / 'upload')
    ALGORITHM: str = "HS256"
    DB_NAME: str = SharedConfig.DB_NAME
    BASE_URL: str = 'mysql+asyncmy://%s:%s@%s:3306/%s?charset=utf8'
    SQLALCHEMY_DATABASE_URI: str = BASE_URL % (os.getenv('MYSQL_USER'), os.getenv('MYSQL_PASSWORD'), os.getenv('MYSQL_HOST'), DB_NAME)
    SESSION_COOKIE_DOMAIN: str = 'localhost'
    APP_URI: str = f'{os.getenv("HTTP_SCHEMA", "http://")}{os.getenv("APP_DOMAIN", "127.0.0.1")}:{os.getenv("APP_PORT", "39015")}'

    model_config = SettingsConfigDict(env_file=Path(__file__).parents[1] / '.env', extra='ignore')

config = Config() # pyright:ignore