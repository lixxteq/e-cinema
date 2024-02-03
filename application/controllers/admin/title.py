from utils import CoverManager, Validator, flash_alert, access_guard
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
    return render_template('admin/title.html', media_id=media_id)

@controller.route('add', methods=['GET', 'POST'])
@login_required
@access_guard(current_user, 'administrator')
def add():
    form = TitleAddForm()
    if request.method == 'GET':
        return render_template('admin/title_add.html', form=form) # TODO
    if request.method == 'POST':
        if not form.validate_on_submit():
            flash_alert('Не все параметры заполнены, повторите попытку', 'danger')
            return redirect(url_for('admin.title.add'))
        cover = CoverManager(form.cover_file.data).save()
        # media = Media(
        #     category = form.category.data,
        #     name = form.name.data,
        #     description = clean(form.description.data or ''),
        #     year = form.year.data,
        #     age_rate = form.age_rate.data if form.age_rate.data != 0 else None,
        #     publisher = form.publisher.data if form.publisher.data else None,
        #     country_id = form.country.data.id if form.country.data else None,
        #     genres = form.genres.data,
        #     cover = cover
        # )
        media = Media()
        form.populate_obj(media)
        media.description = clean(media.description)
        media.cover = cover

        db.session.add(media)
        db.session.commit()
        flash_alert(f'«{media.name}» добавлено в каталог', 'success')
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

        # description = clean(str(request.form.get('description')))
        # year = request.form.get('year')
        # pages = request.form.get('pages')
        # publisher = request.form.get('publisher')
        # genres = request.form.getlist('genre_list')
        # cover_file = request.files.get('cover_file')
        # cover = None
        # if not (name and description and year and pages and publisher):

        # if cover_file:
            # cover = CoverManager(cover_file).save()
            # if not cover:
                # return redirect(url_for('books.edit', book_id=book.id))
        # selected_genres = db.session.scalars(select(Genre).where(Genre.id.in_(map(int, genres))))
        # book = Book(name=name, description=description, year=int(year), pages=int(pages), publisher=publisher, cover_id = cover.id)
        # book.name = name
        # book.description = description
        # book.year = int(year)
        # book.pages = int(pages)
        # book.publisher = publisher
        # book.genres = []
        # for g in selected_genres:
            # book.genres.append(g)
        # if cover: book.cover = cover

        db.session.commit()
        flash_alert(f'«{media.name}» успешно отредактировано', 'success')
    return redirect(url_for('admin.title.view', media_id=media_id))

@controller.route('<int:media_id>/delete', methods=['DELETE'])
@login_required
@access_guard(current_user, 'administrator')
def delete(media_id):
    if request.method == 'DELETE':
        media = db.session.scalar(select(Media).where(Media.media_id == media_id))
        if not media:
            flash_alert('Такой книги не существует или информация о ней недоступна', 'danger')
            return redirect(url_for('index'))
        # CoverManager.delete(media.cover)
        db.session.delete(media)
        db.session.commit()
        
        flash_alert('Книга успешно удалена!', 'success')
    return redirect(url_for('index'))