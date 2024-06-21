from flask_jwt_extended import jwt_required, current_user
from ...utils import CoverManager, Validator, flash_alert, access_guard
from ....models import Genre, User, Media, Cover, Review
from flask import Blueprint, render_template, redirect, url_for, flash, request
# from flask_login import LoginManager, login_required
from sqlalchemy import select
from ...values import ACCESS_LEVEL_MAP
from nh3 import clean
from os import path
from markdown import markdown
from ...app import db


controller = Blueprint('admin', __name__, url_prefix='/admin')
from .title import controller as admin_title_bp
from .service import controller as service_bp
controller.register_blueprint(admin_title_bp)
controller.register_blueprint(service_bp)

@controller.route('/')
@jwt_required(optional=False)
def index():
    return render_template('admin/index.html')