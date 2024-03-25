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

    model_config = SettingsConfigDict(env_file=Path(__file__).parents[1] / '.env', extra='ignore')

config = Config() # pyright:ignore