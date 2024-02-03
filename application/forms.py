from flask_wtf import FlaskForm
from flask_wtf.file import FileField
from sqlalchemy import select
from wtforms import StringField, TextAreaField, IntegerField, BooleanField, SelectField, RadioField
from wtforms.validators import InputRequired, Length, NumberRange, DataRequired, Optional
from wtforms_sqlalchemy.orm import QuerySelectMultipleField, QuerySelectField
from datetime import datetime
from models import Genre, Country
from app import db

def query_genres():
    return db.session.scalars(select(Genre))

def query_countries():
    return db.session.scalars(select(Country))

class TitleAddForm(FlaskForm):
    category = RadioField('Category', validators=[InputRequired()], choices=[('movie', 'Movie'), ('show', 'Show')])
    name = StringField('Name', validators=[InputRequired(), Length(min=3, max=100, message='Name length should be between %(min)d and %(max)d characters')])
    description = TextAreaField('Title description', validators=[InputRequired()])
    year = IntegerField('Release year', validators=[InputRequired(), NumberRange(min=1900, max=datetime.now().year, message='Year should be between %(min)d and %(max)d')])
    age_rate = RadioField('Age rate', validators=[Optional()], choices=[(0, 'None'), (6, '6+'), (12, '12+'), (16, '16+'), (18, '18+')])
    publisher = StringField('Publisher', validators=[Optional(), Length(min=3, max=50, message='Publisher length should be between %(min)d and %(max)d characters')])
    genres = QuerySelectMultipleField('Genres', query_factory=query_genres, get_label='name')
    country = QuerySelectField('Country', query_factory=query_countries, allow_blank=True, get_label='name')
    cover_file = FileField('Title cover image', validators=[InputRequired()])

class TitleEditForm(FlaskForm):
    category = RadioField('Category', validators=[InputRequired()], choices=[('movie', 'Movie'), ('show', 'Show')])
    name = StringField('Name', validators=[InputRequired(), Length(min=3, max=100, message='Name length should be between %(min)d and %(max)d characters')])
    description = TextAreaField('Title description', validators=[InputRequired()])
    year = IntegerField('Release year', validators=[InputRequired(), NumberRange(min=1900, max=datetime.now().year, message='Year should be between %(min)d and %(max)d')])
    age_rate = RadioField('Age rate', validators=[Optional()], choices=[(0, 'None'), (6, '6+'), (12, '12+'), (16, '16+'), (18, '18+')])
    publisher = StringField('Publisher', validators=[Optional(), Length(min=3, max=50, message='Publisher length should be between %(min)d and %(max)d characters')])
    genres = QuerySelectMultipleField('Genres', query_factory=query_genres, get_label='name')
    # cover
    country = QuerySelectField('Country', query_factory=query_countries, allow_blank=True, get_label='name')
    cover_file = FileField('Title cover image', validators=[Optional()])