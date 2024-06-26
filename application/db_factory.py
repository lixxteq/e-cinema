from collections.abc import AsyncGenerator
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import MetaData, create_engine, text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import declarative_base
from .wsgi_app.config import Config
from flask_migrate import Migrate
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

Base = declarative_base(
    metadata=MetaData(naming_convention={
        "ix": 'ix_%(column_0_label)s',
        "uq": "uq_%(table_name)s_%(column_0_name)s",
        "ck": "ck_%(table_name)s_%(constraint_name)s",
        "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
        "pk": "pk_%(table_name)s"
    }))

class FlaskDatabase(SQLAlchemy):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs, model_class=Base)
        self._app: Flask = kwargs['app']
        self._create_db()

    def _create_db(self):
        with create_engine(self._app.config['ENGINE_URI']).connect() as connection:
            connection.execute(text(f'CREATE DATABASE IF NOT EXISTS {Config.DB_NAME}'))

    def init_schema(self):
        with self._app.app_context():
            self.create_all()

    def init_migrate(self):
        return Migrate(self._app, self)

class FastAPIDatabase():
    def __init__(self, engine_uri):
        self.engine = create_async_engine(engine_uri)
        self.factory = async_sessionmaker(bind=self.engine)
    
    async def _retrieve_session(self) -> AsyncGenerator[AsyncSession, None]:
        async with self.factory() as session:
            try:
                yield session
                await session.commit()
            except SQLAlchemyError as error:
                await session.rollback()
                raise error
    
    @property
    def session(self):
        return self._retrieve_session