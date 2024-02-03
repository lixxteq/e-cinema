import datetime
import re
from typing import List, Literal, get_args
from functools import reduce
from flask import url_for
from values import ACCESS_LEVEL_MAP
from db_factory import Base
import sqlalchemy as alc
from sqlalchemy import BigInteger, Integer, String, Text, ForeignKey, DateTime, Enum, UUID, func
from sqlalchemy.orm import Mapped, mapped_column, relationship, validates
from flask_bcrypt import generate_password_hash, check_password_hash
from flask_login import UserMixin
from app import db

Category = Literal['movie', 'show']

class MediaSource(Base):
    __tablename__ = 'media_sources'

    composite_id: Mapped[str] = mapped_column(String(30), primary_key=True, unique=True) # movie id (ex: 124) / show id with season and episode number suffix (ex: 125_1_6)
    # prefix: Mapped[str] = mapped_column(String, nullable=False)
    source: Mapped[str] = mapped_column(String(255), nullable=False)



media_genre_m2m = db.Table(
    'media_genre',
    Base.metadata,
    alc.Column('media_id', ForeignKey('media.media_id', ondelete='CASCADE'), primary_key=True),
    alc.Column('genre_id', ForeignKey('genres.id', ondelete='CASCADE'), primary_key=True),
)

class Genre(Base):
    __tablename__ = 'genres'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)

    media: Mapped[List['Media']] = relationship(secondary=media_genre_m2m, back_populates='genres')

class Country(Base):
    __tablename__ = 'countries'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    code: Mapped[str] = mapped_column(String(3), nullable=False, unique=True)
    name: Mapped[str] = mapped_column(String(30), nullable=False)

    media: Mapped[List['Media']] = relationship(back_populates='country')

class Media(Base):
    __tablename__ = 'media'

    media_id: Mapped[int] = mapped_column(BigInteger, primary_key=True, default=func.uuid_short())
    category: Mapped[Category] = mapped_column(Enum(*get_args(Category), name='category', create_constraint=True, validate_strings=True))
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    year: Mapped[int] = mapped_column(Integer, nullable=False)
    age_rate: Mapped[int] = mapped_column(Integer, nullable=True)
    publisher: Mapped[str] = mapped_column(String(50), nullable=True)

    # cover_id: Mapped[int] = mapped_column(ForeignKey(Cover.id, ondelete='SET NULL', onupdate='CASCADE'), nullable=True)
    country_id: Mapped[str] = mapped_column(ForeignKey(Country.id, ondelete='SET NULL', onupdate='CASCADE'), nullable=True)

    rating_summary: Mapped[int] = mapped_column(db.Integer, nullable=False, default=0)
    rating_amount: Mapped[int] = mapped_column(db.Integer, nullable=False, default=0)

    cover: Mapped['Cover'] = relationship(back_populates='media', lazy='subquery')
    country: Mapped['Country'] = relationship(back_populates='media')
    genres: Mapped[List['Genre']] = relationship(secondary=media_genre_m2m, back_populates='media')
    reviews: Mapped[List['Review']] = relationship(back_populates='media', cascade='all, delete')

    def get_rating(self):
        if self.rating_amount == 0:
            return 0
        return round(self.rating_summary / self.rating_amount, 1)

    # TODO: content path 
    def get_cover_url(self):
        return url_for('static', filename=f'upload/{self.cover.filename}')

class Cover(Base):
    __tablename__ = 'covers'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    mimetype: Mapped[str] = mapped_column(String(15), nullable=False)
    md5_hash: Mapped[str] = mapped_column(String(32), nullable=False)
    filename: Mapped[str] = mapped_column(String(50), nullable=False)
    media_id: Mapped[int] = mapped_column(ForeignKey(Media.media_id, ondelete='SET NULL', onupdate='CASCADE'), nullable=True) # TODO: cascade delete? not sure

    media: Mapped['Media'] = relationship(back_populates='cover')

class Movie(Base):
    __tablename__ = 'movies'

    id: Mapped[int] = mapped_column(ForeignKey(Media.media_id, ondelete='CASCADE', onupdate='CASCADE'), primary_key=True)
    duration: Mapped[int] = mapped_column(Integer, nullable=True)

    @property
    def source_composite_id(self) -> str:
        return str(self.id)

class Show(Base):
    __tablename__ = 'shows'

    id: Mapped[int] = mapped_column(ForeignKey(Media.media_id, ondelete='CASCADE', onupdate='CASCADE'), primary_key=True)

    seasons: Mapped[List['Season']] = relationship(back_populates='show')

    def seasons_count(self):
        return self.seasons.__len__()
    
    def episodes_count(self):
        return reduce(lambda t, c: t + c.episodes_count(), self.seasons, 0)

class Season(Base):
    __tablename__ = 'seasons'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    number: Mapped[int] = mapped_column(Integer, nullable=False)
    show_id: Mapped[int] = mapped_column(ForeignKey(Show.id, ondelete='CASCADE', onupdate='CASCADE'), nullable=False)

    show: Mapped['Show'] = relationship(back_populates='seasons')
    episodes: Mapped[List['Episode']] = relationship(back_populates='season')

    def episodes_count(self):
        return self.episodes.__len__()

class Episode(Base):
    __tablename__ = 'episodes'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    number: Mapped[int] = mapped_column(Integer, nullable=False)
    season_id: Mapped[int] = mapped_column(ForeignKey(Season.id, ondelete='CASCADE', onupdate='CASCADE'), nullable=False)

    season: Mapped['Season'] = relationship(back_populates='episodes')

    @property
    def source_composite_id(self) -> str:
        return f'{self.season.show_id}_{self.season.number}_{self.number}'

class Role(Base):
    __tablename__ = 'roles'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(20), nullable=False, unique=True)
    description: Mapped[str] = mapped_column(Text, nullable=False)

    # users: Mapped[List['User']] = relationship(back_populates='role')

class User(Base, UserMixin):
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    login: Mapped[str] = mapped_column(String(50), nullable=False, unique=True)
    display_name: Mapped[str] = mapped_column(String(100), nullable=False)
    email: Mapped[str] = mapped_column(String(320), nullable=False, unique=True)
    password_hash: Mapped[str] = mapped_column(String(100), nullable=False)
    # last_name: Mapped[str] = mapped_column(String(40), nullable=False)
    # first_name: Mapped[str] = mapped_column(String(40), nullable=False)
    # middle_name: Mapped[Optional[str]] = mapped_column(String(40))
    role_id: Mapped[int] = mapped_column(ForeignKey(Role.id), nullable=False)
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False, server_default=alc.sql.func.now())

    def set_password(self, password):
        self.password_hash = generate_password_hash(password).decode()

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    @property
    def access_level(self):
        return ACCESS_LEVEL_MAP[self.role.name]
    
    # TODO: error check
    def has_access(self, req_access_level):
        return self.access_level >= ACCESS_LEVEL_MAP[req_access_level]
    
    # TODO: extend validation
    @validates('email')
    def validate_email(self, key, value):
        if re.match(r'[a-zA-Z0-9.!#$%&’*+/=?^_`{|}~-]+@[a-zA-Z0-9-]+(?:\.[a-zA-Z0-9-]+)*', value):
            return value
        raise ValueError('User.validates(email)')
    
    @validates('login')
    def validate_login(self, key, value):
        if re.match(r'(?=.*\d)(?=.*[a-zA-Z]).{8,}', value):
            return value
        raise ValueError('User.validates(login)')

    reviews: Mapped[List['Review']] = relationship(back_populates='user')
    role: Mapped['Role'] = relationship('Role')

class Review(Base):
    __tablename__ = 'reviews'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    media_id: Mapped[int] = mapped_column(ForeignKey(Media.media_id, ondelete='CASCADE', onupdate='CASCADE'), nullable=False)
    user_id: Mapped[int] = mapped_column(ForeignKey(User.id, ondelete='CASCADE'), nullable=False)
    rating: Mapped[int] = mapped_column(Integer, nullable=False)
    text: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False, server_default=alc.sql.func.now())

    user: Mapped['User'] = relationship(back_populates='reviews')
    media: Mapped['Media'] = relationship(back_populates='reviews')

db.init_schema()