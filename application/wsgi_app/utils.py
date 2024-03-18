from hashlib import md5
from uuid import uuid4
from flask import flash, url_for, request, redirect, session
from markupsafe import Markup
from nh3 import clean
from sqlalchemy import select
from werkzeug.datastructures import FileStorage
from .values import ACCESS_LEVEL_MAP, ALLOWED_MIME_TYPES, FLASH_DURATION
from .models import Cover, db
from werkzeug.utils import secure_filename
from os import path, remove
from flask_login import AnonymousUserMixin, current_user
from typing import Sequence, TypeVar
from sqlalchemy.engine.result import _RowData
from functools import wraps
T = TypeVar('T', bound=_RowData)

def flash_alert(message, category):
    """Inject stylized bootstrap alert HTML in template's alert block"""
    alert = Markup(
        f"""
    <div class="alert alert-{category} alert-dismissible fade show position-sticky w-25 mt-3 ms-3" role="alert" style="opacity: 0.98; z-index: 10000">
      {message}
    </div>
    <script>
        setTimeout(() => document.getElementById('alert-block').remove(), {FLASH_DURATION});
    </script>
    """
    )
    flash(alert, category)

# TODO: emits exception on empty / unsatisfying result
def seq_fetch_one(sequence: Sequence[T], key: str, value) -> T:
    """Iterate through sequence of scalar values and select one satisfying requirement [key:value]"""
    return next(filter(lambda o: getattr(o, key) == value, sequence))

class CoverManager:
    """Implements methods for working with Cover model objects"""
    def __init__(self, cover_file: FileStorage):
        self.cover_file = cover_file

    def save(self):
        cover = self.find_by_hash()
        if (cover):
            return cover
        self.filename = uuid4().__str__() + secure_filename(self.cover_file.filename) if self.cover_file.filename else uuid4().__str__()
        if self.filename.__len__() > 50: self.filename = self.filename[self.filename.__len__()-49:self.filename.__len__()]
        self.fs_save()
        self.db_save()
        return db.session.scalar(select(Cover).where(Cover.md5_hash == self.hash))

    def fs_save(self):
        self.cover_file.save(path.join('static', 'upload', self.filename))
                             
    def db_save(self):
        db.session.add(Cover(filename=self.filename, mimetype=self.cover_file.mimetype, md5_hash=self.hash))
        db.session.commit()
    
    # def fs_delete(self):


    def find_by_hash(self):
        self.hash = md5(self.cover_file.stream.read()).hexdigest()
        self.cover_file.stream.seek(0)
        return db.session.scalar(select(Cover).where(Cover.md5_hash == self.hash))
    
    @staticmethod
    def delete(cover: Cover):
        cover_path = path.join(path.dirname(path.abspath(__file__)), 'static', 'upload', cover.filename)
        remove(cover_path)
        db.session.delete(cover)
        db.session.commit()

class Validator:
    """Implements static methods for validating and formatting user form-data input"""
    @staticmethod
    def validate_rating(form_select):
        if form_select == None:
            return None
        rating = int(form_select)
        if not 1 <= rating <= 5:
            return None
        return rating
    
    @staticmethod
    def validate_review(form_textarea):
        if form_textarea == None or form_textarea == '':
            return None
        return clean(form_textarea)
    
    @staticmethod
    def validate_email(form_email):
        if form_email == None or form_email == '':
            return None
        return form_email
    
    @staticmethod
    def validate_cover(form_cover_file: FileStorage):
        return True if form_cover_file.mimetype in ALLOWED_MIME_TYPES else False
    
def access_guard(current_user, req_access_level):
    """Access level guard decorator. Responses with error if authenticated user has no access to specified endpoint"""
    def decorator(f):
        @wraps(f)
        def wrapped(*args, **kwargs):
            if not current_user or current_user.is_anonymous or not current_user.has_access(req_access_level):
                flash_alert('У вас недостаточно прав для выполнения данного действия', 'danger')
                return redirect(url_for('index'))

            return f(*args, **kwargs)
        return wrapped
    return decorator

def flash_errors(form):
    """Directs WTForms errors to flash_alert"""
    for field, errors in form.errors.items():
        for error in errors:
            flash_alert(f'{getattr(form, field).label.text}: {error}', 'danger')