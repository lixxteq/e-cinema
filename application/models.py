import datetime
from typing import List, Optional
from flask import url_for
from db_factory import Base
import sqlalchemy as alc
from sqlalchemy import Integer, String, Text, ForeignKey, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from flask_bcrypt import generate_password_hash, check_password_hash
from flask_login import UserMixin
from app import db

class Cover(Base):
    __tablename__ = 'covers'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    mimetype: Mapped[str] = mapped_column(String(15), nullable=False)
    md5_hash: Mapped[str] = mapped_column(String(32), nullable=False)
    filename: Mapped[str] = mapped_column(String(50), nullable=False)

    book: Mapped['Book'] = relationship(back_populates='cover')

book_genre_m2m = db.Table(
    'book_genre',
    Base.metadata,
    alc.Column('book_id', ForeignKey('books.id', ondelete='CASCADE'), primary_key=True),
    alc.Column('genre_id', ForeignKey('genres.id', ondelete='CASCADE'), primary_key=True),
)

class Genre(Base):
    __tablename__ = 'genres'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)

    books: Mapped[List['Book']] = relationship(secondary=book_genre_m2m, back_populates='genres')

class Book(Base):
    __tablename__ = 'books'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    year: Mapped[int] = mapped_column(Integer, nullable=False)
    publisher: Mapped[str] = mapped_column(String(50), nullable=False)
    pages: Mapped[int] = mapped_column(Integer, nullable=False)
    cover_id: Mapped[int] = mapped_column(ForeignKey(Cover.id, ondelete='CASCADE'), nullable=False)
    rating_summary: Mapped[int] = mapped_column(db.Integer, nullable=False, default=0)
    rating_amount: Mapped[int] = mapped_column(db.Integer, nullable=False, default=0)

    def get_rating(self):
        if self.rating_amount == 0:
            return 0
        return self.rating_summary / self.rating_amount

    def get_cover_url(self):
        return url_for('static', filename=f'upload/{self.cover.filename}')
    
    cover: Mapped['Cover'] = relationship(back_populates='book', lazy='subquery')
    genres: Mapped[List['Genre']] = relationship(secondary=book_genre_m2m, back_populates='books')
    reviews: Mapped[List['Review']] = relationship(back_populates='book')

class Role(Base):
    __tablename__ = 'roles'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(20), nullable=False, unique=True)
    description: Mapped[str] = mapped_column(Text, nullable=False)

class User(Base, UserMixin):
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    login: Mapped[str] = mapped_column(String(30), nullable=False, unique=True)
    password_hash: Mapped[str] = mapped_column(String(100), nullable=False)
    last_name: Mapped[str] = mapped_column(String(40), nullable=False)
    first_name: Mapped[str] = mapped_column(String(40), nullable=False)
    middle_name: Mapped[Optional[str]] = mapped_column(String(40))
    role_id: Mapped[int] = mapped_column(ForeignKey(Role.id), nullable=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password).decode()

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    reviews: Mapped[List['Review']] = relationship(back_populates='user')

class Review(Base):
    __tablename__ = 'reviews'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    book_id: Mapped[int] = mapped_column(ForeignKey(Book.id, ondelete='CASCADE'), nullable=False)
    user_id: Mapped[int] = mapped_column(ForeignKey(User.id, ondelete='CASCADE'), nullable=False)
    rating: Mapped[int] = mapped_column(Integer, nullable=False)
    text: Mapped[str] = mapped_column(Text, nullable=False)
    date: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False, server_default=alc.sql.func.now())

    user: Mapped['User'] = relationship(back_populates='reviews')
    book: Mapped['Book'] = relationship(back_populates='reviews')

db.init_schema()