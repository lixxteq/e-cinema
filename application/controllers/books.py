from utils import CoverManager, flash_alert, get_access_level, is_anonimous, get_user_id
from models import Genre, db, User, Book, Cover, Review
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import LoginManager, login_required, current_user
from sqlalchemy import select
from values import VISITOR_ACCESS_LEVEL, ADMIN_ACCESS_LEVEL, MODERATOR_ACCESS_LEVEL
import bleach
from os import path
from markdown import markdown

controller = Blueprint('books', __name__, url_prefix='/books')

def has_access(user, required_role):
    return True if user._get_current_object().role_id >= required_role else False

@controller.route('create', methods=['GET', 'POST'])
@login_required
def create():
    if not has_access(current_user, ADMIN_ACCESS_LEVEL):
        flash_alert('У вас недостаточно прав для выполнения данного действия', 'danger')
        return redirect(url_for('index'))
    if request.method == 'GET':
        return render_template('book_create.html', genres=db.session.scalars(select(Genre)).all()) # scalar dehaviour?
    if request.method == 'POST':
        name = request.form.get('name')
        description = bleach.clean(str(request.form.get('description')))
        year = request.form.get('year')
        pages = request.form.get('pages')
        publisher = request.form.get('publisher')
        genres = request.form.getlist('genre_list')
        cover_file = request.files.get('cover_file')
        print(name, description, year, pages, publisher, cover_file)
        if not (name and description and year and pages and publisher and cover_file):
            flash_alert('Не все параметры заполнены, повторите попытку', 'danger')
            return redirect(url_for('books.create'))
        cover = CoverManager(cover_file).save()
        if not cover:
            return redirect(url_for('books.create'))
        selected_genres = db.session.scalars(select(Genre).where(Genre.id.in_(map(int, genres))))
        book = Book(name=name, year=int(year), pages=int(pages), publisher=publisher, cover_id = cover.id)
        for g in selected_genres:
            book.genres.append(g)
        db.session.add(book)
        db.session.commit()
        flash_alert('Книга добавлена!', 'success')
    return redirect(url_for('index'))

@controller.route('view/<int:book_id>', methods=['GET', 'POST'])
def view(book_id):
    book = db.session.scalar(select(Book).where(Book.id == book_id))
    if not book:
        flash_alert('Такой книги не существует или информация о ней недоступна', 'danger')
        return redirect(url_for('index'))
    if request.method == 'GET':
        genres = book.genres
        cover_url = url_for('static', filename=f'upload/{book.cover.filename}')
        description = markdown(book.description)
        raw_reviews = db.session.scalars(select(Review).where(Review.book_id == book_id)).all()
        user_review = None
        reviews = []
        if raw_reviews.__len__() > 0:
            user_review = [review for review in raw_reviews if not is_anonimous() and review.user_id == get_user_id()]
            user_review = user_review[0] if user_review.__len__() > 0 else None
            for rev in raw_reviews:
                if rev.user_id != get_user_id():
                    reviews.append({
                        'user': f'{rev.user.first_name} {rev.user.last_name}',
                        'text': markdown(rev.text),
                        'rating': rev.rating
                    })
        return render_template('book_view.html', genres=genres, cover_url=cover_url, description=description, reviews=reviews, book=book, user_review=user_review, is_anonimous=is_anonimous, access_level=get_access_level())
    if request.method == 'POST':
        if is_anonimous():
            flash_alert('Авторизуйтесь для добавления отзыва', 'danger')
            redirect(url_for('auth.login'))
        user_id = get_user_id()
        text = bleach.clean(str(request.form.get('review')))
        rating = int(request.form.get('rating_select')) if request.form.get('rating_select') else None # type: ignore
        # Если отзыв пользователя уже существует, не дает создать новый
        if db.session.scalar(select(Review).where(Review.user_id == user_id)):
            flash_alert('Произошла ошибка', 'danger')
            return redirect(url_for('index'))
        if rating:
            book.rating_amount += 1
            book.rating_summary += rating
        db.session.add(Review(user_id=user_id, book_id=book_id, rating=rating, text=text))
        db.session.commit()
        flash_alert('Ваш отзыв был добавлен', 'success')
    return redirect(url_for('books.view', book_id=book.id))

@controller.route('edit/<int:book_id>', methods=['GET', 'POST'])
@login_required
def edit(book_id):
    if not has_access(current_user, MODERATOR_ACCESS_LEVEL):
        flash_alert('У вас недостаточно прав для выполнения данного действия', 'danger')
        return redirect(url_for('index'))
    book = db.session.scalar(select(Book).where(Book.id == book_id))
    if not book:
        flash_alert('Такой книги не существует или информация о ней недоступна', 'danger')
        return redirect(url_for('index'))
    if request.method == 'GET':
        genres = db.session.scalars(select(Genre)).all()
        return render_template('book_edit.html', book=book, genres=genres)
    if request.method == 'POST':
        name = request.form.get('name')
        description = bleach.clean(str(request.form.get('description')))
        year = request.form.get('year')
        pages = request.form.get('pages')
        publisher = request.form.get('publisher')
        genres = request.form.getlist('genre_list')
        cover_file = request.files.get('cover_file')
        cover = None
        if not (name and description and year and pages and publisher):
            flash_alert('Не все параметры заполнены, повторите попытку', 'danger')
            return redirect(url_for('books.edit', book_id=book.id))
        if cover_file:
            cover = CoverManager(cover_file).save()
            if not cover:
                return redirect(url_for('books.edit', book_id=book.id))
        selected_genres = db.session.scalars(select(Genre).where(Genre.id.in_(map(int, genres))))
        # book = Book(name=name, description=description, year=int(year), pages=int(pages), publisher=publisher, cover_id = cover.id)
        book.name = name
        book.description = description
        book.year = int(year)
        book.pages = int(pages)
        book.publisher = publisher
        book.genres = []
        for g in selected_genres:
            book.genres.append(g)
        if cover: book.cover = cover

        db.session.commit()
        flash_alert('Книга отредактирована!', 'success')
    return redirect(url_for('books.view', book_id=book_id))

@controller.route('/delete/<int:book_id>', methods=['POST'])
@login_required
def delete(book_id):
    if not has_access(current_user, ADMIN_ACCESS_LEVEL):
        flash_alert('У вас недостаточно прав для выполнения данного действия', 'danger')
        return redirect(url_for('index'))
    if request.method == 'POST':
        book = db.session.scalar(select(Book).where(Book.id == book_id))
        if not book:
            flash_alert('Такой книги не существует или информация о ней недоступна', 'danger')
            return redirect(url_for('index'))
        for rev in book.reviews:
            db.session.delete(rev)
        db.session.delete(book)
        db.session.commit()
        CoverManager.delete(book.cover)
        flash_alert('Книга успешно удалена!', 'success')
    return redirect(url_for('index'))
