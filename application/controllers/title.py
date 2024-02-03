from utils import CoverManager, Validator, flash_alert, access_guard
from models import Genre, db, User, Media, Cover, Review
from flask import Blueprint, render_template, redirect, url_for, request, abort
from flask_login import login_required
from sqlalchemy import select
from nh3 import clean
from markdown import markdown
from app import current_user

controller = Blueprint('title', __name__, url_prefix='/title')

# def has_access(user, required_role):
#     return True if user._get_current_object().role_id >= required_role else False

@controller.route('<int:media_id>', methods=['GET', 'POST'])
def view(media_id: int):
    media = db.session.scalar(select(Media).where(Media.media_id == media_id))
    current_user_review = db.session.scalar(select(Review).where(Review.user_id == current_user.id).where(Review.media_id == media_id)) if not current_user.is_anonymous else None
    if not media:
        # return redirect(url_for('not_found'))
        abort(404)
    if request.method == 'GET':
        cover_url = url_for('static', filename=f'upload/{media.cover.filename}') if media.cover else url_for('static', filename='image/default_cover.png') # needs refactoring
        description = markdown(media.description)
        reviews = list(db.session.scalars(select(Review).where(Review.media_id == media_id)).all()) # filter by datetime
        # current_user_review = next((r for r in reviews if r.user_id == current_user.id), None) # performance?
        if current_user_review:
            reviews.remove(current_user_review) # inspect ORM behaviour
        templated_reviews = [ # created at field
            {
                'user': rev.user.display_name,
                'text': markdown(rev.text),
                'rating': rev.rating
            } for rev in reviews
        ]
        return render_template('title/view.html', cover_url=cover_url, description=description, reviews=templated_reviews, media=media, user_review=current_user_review, markdown=markdown)
    if request.method == 'DELETE':
        if current_user_review:
            db.session.delete(current_user_review)
            media.rating_amount -= 1
            media.rating_summary -= current_user_review.rating
            db.session.commit()
            flash_alert('Ваш отзыв был удален', 'success')
        else:
            flash_alert('Произошла ошибка: вы не можете удалить отзыв', 'danger')
    if request.method == 'POST':
        if current_user.is_anonymous:
            flash_alert('Авторизуйтесь для добавления отзыва', 'danger')
            return redirect(url_for('auth.login'))
        text = Validator.validate_review(request.form.get('review'))
        rating = Validator.validate_rating(request.form.get('rating_select'))
        
        if rating and text:
            # Review editing functionality
            if current_user_review: # date modification?
                media.rating_summary += rating - current_user_review.rating # inspect
                current_user_review.rating = rating
                current_user_review.text = text
                db.session.commit()
                flash_alert('Ваш отзыв был изменен', 'success')
            else:
                media.rating_amount += 1
                media.rating_summary += rating
                db.session.add(Review(user_id=current_user.id, media_id=media.media_id, rating=rating, text=text))
                db.session.commit()
                flash_alert('Ваш отзыв был добавлен', 'success') 
        else:
            flash_alert('Произошла ошибка при добавлении отзыва', 'danger')
            return redirect(url_for('index'))
    return redirect(url_for('title.view', media_id=media_id))
