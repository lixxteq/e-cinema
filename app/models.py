import datetime
from typing import Optional
from db_factory import database_factory
import sqlalchemy as alc
from sqlalchemy import Integer, String, Text, ForeignKey, DateTime
from sqlalchemy.orm import Mapped, mapped_column
from flask_bcrypt import generate_password_hash, check_password_hash
from flask_login import UserMixin

db = database_factory()

class Cover(db.Model):
    __tablename__ = 'covers'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    mimetype: Mapped[str] = mapped_column(String(15), nullable=False)
    md5_hash: Mapped[str] = mapped_column(String(32), nullable=False)

class Book(db.Model):
    __tablename__ = 'books'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    year: Mapped[int] = mapped_column(Integer, nullable=False)
    publisher: Mapped[str] = mapped_column(String(50), nullable=False)
    pages: Mapped[int] = mapped_column(Integer, nullable=False)
    cover_id: Mapped[int] = mapped_column(ForeignKey(Cover.id), nullable=False)

class Genre(db.Model):
    __tablename__ = 'genres'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)

book_genre_m2m = db.Table(
    'book_genre',
    alc.Column('book_id', ForeignKey(Book.id), primary_key=True),
    alc.Column('genre_id', ForeignKey(Genre.id), primary_key=True)
)

class Role(db.Model):
    __tablename__ = 'roles'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(20), nullable=False, unique=True)
    description: Mapped[str] = mapped_column(Text, nullable=False)

class User(db.Model, UserMixin):
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

class Review(db.Model):
    __tablename__ = 'reviews'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    book_id: Mapped[int] = mapped_column(ForeignKey(Book.id), nullable=False)
    user_id: Mapped[int] = mapped_column(ForeignKey(User.id), nullable=False)
    rating: Mapped[int] = mapped_column(Integer, nullable=False)
    text: Mapped[str] = mapped_column(Text, nullable=False)
    date: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False, server_default=alc.sql.func.now())