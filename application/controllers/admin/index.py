from utils import CoverManager, Validator, flash_alert, access_guard
from models import Genre, db, User, Media, Cover, Review
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import LoginManager, login_required
from sqlalchemy import select
from values import ACCESS_LEVEL_MAP
from nh3 import clean
from os import path
from markdown import markdown
from app import current_user

controller = Blueprint('admin', __name__, url_prefix='/admin')
from controllers.admin.title import controller as admin_title_bp
controller.register_blueprint(admin_title_bp)

@controller.route('/')
def index():
    return render_template('admin/index.html')