from hashlib import md5
from uuid import uuid4
from flask import flash
from markupsafe import Markup
from sqlalchemy import select
from werkzeug.datastructures import FileStorage
from values import VISITOR_ACCESS_LEVEL
from models import Cover, db
from werkzeug.utils import secure_filename
from os import path, remove
from flask_login import current_user, AnonymousUserMixin

# Использует заготовленный HTML для отображения flash-сообщений в виде само-исчезающих алертов
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


def get_access_level():
    if (isinstance(current_user._get_current_object(), AnonymousUserMixin)):
        return VISITOR_ACCESS_LEVEL
    return current_user._get_current_object().role_id

# Проверка анонимности текущего пользователя через принадлежность к UserMixin классу анонимного пользователя
def is_anonimous():
    if (isinstance(current_user._get_current_object(), AnonymousUserMixin)):
        return True
    return False

def get_user_id():
    if not is_anonimous():
        return current_user._get_current_object().id
    return None

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