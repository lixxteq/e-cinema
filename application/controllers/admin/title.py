from utils import CoverManager, Validator, flash_alert, access_guard, flash_errors
from models import Genre, db, User, Media, Cover, Review
from flask import Blueprint, render_template, redirect, url_for, request, abort
from flask_login import login_required
from sqlalchemy import select
from values import ACCESS_LEVEL_MAP
from nh3 import clean
from markdown import markdown
from app import current_user
from forms import TitleAddForm, TitleEditForm

controller = Blueprint('title', __name__, url_prefix='/title')

@controller.route('<int:media_id>')
@login_required
@access_guard(current_user, 'moderator')
def view(media_id):
    media = db.session.scalar(select(Media).where(Media.media_id == media_id))
    if not media:
        abort(404)
    cover_url = url_for('static', filename=f'upload/{media.cover.filename}') if media.cover else url_for('static', filename='image/default_cover.png') # needs refactoring
    return render_template('admin/title.html', media=media, cover_url=cover_url)

@controller.route('add', methods=['GET', 'POST'])
@login_required
@access_guard(current_user, 'administrator')
def add():
    form = TitleAddForm()
    if request.method == 'GET':
        return render_template('admin/title_add.html', form=form) # TODO
    if request.method == 'POST':
        if not form.validate_on_submit():
            flash_errors(form)
            return redirect(url_for('admin.title.add'))
        cover = CoverManager(form.cover_file.data).save()
        media = Media()
        form.populate_obj(media)
        media.description = clean(media.description)
        media.age_rate = 0 if not media.age_rate else media.age_rate # no protection
        media.cover = cover

        db.session.add(media)
        db.session.commit()
        flash_alert(f'«{media.name}» addded to catalog', 'success')
    return redirect(url_for('index'))

@controller.route('<int:media_id>/edit', methods=['GET', 'POST'])
@login_required
@access_guard(current_user, 'administrator')
def edit(media_id):
    form = TitleEditForm()
    media = db.session.scalar(select(Media).where(Media.media_id == media_id))
    if not media:
        abort(404)
    if request.method == 'GET':
        form.process(obj=media)
        return render_template('admin/title_edit.html', form=form, media_id=media_id)
    if request.method == 'POST':
        if not form.validate_on_submit():
            flash_alert('Не все параметры заполнены, повторите попытку', 'danger')
            return redirect(url_for('admin.title.edit', media_id=media.media_id))
        form.populate_obj(media)
        media.description = clean(media.description)

        if form.cover_file.data:
            cover = CoverManager(form.cover_file.data).save()
            media.cover = cover

        db.session.commit()
        flash_alert(f'«{media.name}» успешно отредактировано', 'success')
    return redirect(url_for('admin.title.view', media_id=media_id))

@controller.route('<int:media_id>/delete', methods=['POST'])
@login_required
@access_guard(current_user, 'administrator')
def delete(media_id):
    if request.method == 'POST':
        media = db.session.scalar(select(Media).where(Media.media_id == media_id))
        if not media:
            flash_alert('Такой книги не существует или информация о ней недоступна', 'danger')
            return redirect(url_for('index'))
        if request.args.get('delete_cover') == '1':
            CoverManager.delete(media.cover)
        db.session.delete(media)
        db.session.commit()
        
        flash_alert('Книга успешно удалена!', 'success')
    return redirect(url_for('index'))