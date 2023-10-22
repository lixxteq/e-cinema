from models import db
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from sqlalchemy import select

controller = Blueprint('books', __name__, url_prefix='/books')

