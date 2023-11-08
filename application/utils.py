from hashlib import md5
from uuid import uuid4
from flask import flash
from markupsafe import Markup
from bleach import clean
from sqlalchemy import select
from werkzeug.datastructures import FileStorage
from models import Cover, db
from werkzeug.utils import secure_filename
from os import path, remove
from flask_login import AnonymousUserMixin, current_user

# Inject styled bootstrap-alert html in template html alert block
def flash_alert(message, category):
    alert = Markup(
        f"""
    <div class="alert alert-{category} alert-dismissible fade show w-25 position-fixed mt-3 ms-3" role="alert" style="opacity: 0.98; z-index: 10000">
      {message}
    </div>
    <script>
        setTimeout(() => document.getElementById('alert-block').remove(), 5000);
    </script>
    """
    )
    flash(alert, category)

class CoverManager:
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