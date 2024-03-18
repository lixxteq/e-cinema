from flask_wtf import FlaskForm
from flask_wtf.file import FileField
from sqlalchemy import select
from wtforms import EmailField, PasswordField, StringField, TextAreaField, IntegerField, BooleanField, SelectField, RadioField, ValidationError
from wtforms.validators import InputRequired, Length, NumberRange, Optional, Regexp, Email
from wtforms_sqlalchemy.orm import QuerySelectMultipleField, QuerySelectField
from datetime import datetime
from .values import ALLOWED_MIME_TYPES
from .models import Genre, Country
from .app import db

def query_genres():
    return db.session.scalars(select(Genre))

def query_countries():
    return db.session.scalars(select(Country))

def validate_cover_mimetype(form, field):
    if not field.data.mimetype in ALLOWED_MIME_TYPES:
        raise ValidationError('Uploaded cover file is not an image')

class TitleAddForm(FlaskForm):
    category = RadioField('Category', validators=[InputRequired()], choices=[('movie', 'Movie'), ('show', 'Show')])
    name = StringField('Name', validators=[InputRequired(), Length(min=3, max=100, message='Name length should be between %(min)d and %(max)d characters')])
    description = TextAreaField('Title description', validators=[InputRequired()])
    year = IntegerField('Release year', validators=[InputRequired(), NumberRange(min=1900, max=datetime.now().year, message='Year should be between %(min)d and %(max)d')])
    age_rate = RadioField('Age rate', default=0, choices=[(0, 'Any'), (6, '6+'), (12, '12+'), (16, '16+'), (18, '18+')])
    publisher = StringField('Publisher', validators=[Optional(), Length(min=3, max=50, message='Publisher length should be between %(min)d and %(max)d characters')])
    genres = QuerySelectMultipleField('Genres', query_factory=query_genres, get_label='name')
    country = QuerySelectField('Country', query_factory=query_countries, allow_blank=True, get_label='name')
    cover_file = FileField('Title cover image', validators=[InputRequired(), validate_cover_mimetype])

class TitleEditForm(FlaskForm):
    category = RadioField('Category', validators=[InputRequired()], choices=[('movie', 'Movie'), ('show', 'Show')])
    name = StringField('Name', validators=[InputRequired(), Length(min=3, max=100, message='Name length should be between %(min)d and %(max)d characters')])
    description = TextAreaField('Title description', validators=[InputRequired()])
    year = IntegerField('Release year', validators=[InputRequired(), NumberRange(min=1900, max=datetime.now().year, message='Year should be between %(min)d and %(max)d')])
    age_rate = RadioField('Age rate', default=0, choices=[(0, 'Any'), (6, '6+'), (12, '12+'), (16, '16+'), (18, '18+')])
    publisher = StringField('Publisher', validators=[Optional(), Length(min=3, max=50, message='Publisher length should be between %(min)d and %(max)d characters')])
    genres = QuerySelectMultipleField('Genres', query_factory=query_genres, get_label='name')
    country = QuerySelectField('Country', query_factory=query_countries, allow_blank=True, get_label='name')
    cover_file = FileField('Title cover image', validators=[Optional(), validate_cover_mimetype])

class RegisterForm(FlaskForm):
    login = StringField('Login', validators=[InputRequired(), Regexp('^(?=.*[A-Za-z0-9]$)[A-Za-z][A-Za-z\d_]{7,20}$', message='Bad input')])
    display_name = StringField('Display name', validators=[InputRequired(), Regexp('^(?=.*[A-Za-z0-9]$)[A-Za-z][A-Za-z\d_]{7,20}$', message='Bad input')])
    email = EmailField('Email', validators=[InputRequired(), Email(message='Email verification error')])
    password = PasswordField('Password', validators=[InputRequired(), Regexp('^((?=\S*?[a-z])(?=\S*?[0-9]).{8,})\S$', message='Bad input')])
    repeat_password = PasswordField('Repeat password', validators=[InputRequired(), Regexp('^((?=\S*?[a-z])(?=\S*?[0-9]).{8,})\S$', message='Bad input')])

class LoginForm(FlaskForm):
    login = StringField('Login or email', validators=[InputRequired(), Regexp('^(?=.*[A-Za-z0-9]$)[A-Za-z][A-Za-z\d_]{7,20}$', message='Bad input')])
    password = PasswordField('Password', validators=[InputRequired(), Regexp('^((?=\S*?[a-z])(?=\S*?[0-9]).{7,})\S$', message='Bad input')])
    remember_me = BooleanField('Remember me', default=False)