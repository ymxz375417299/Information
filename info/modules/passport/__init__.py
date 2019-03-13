# coding=utf-8
from flask import Blueprint

passport_blu = Blueprint('password', __name__, url_prefix='/passport')

from . import views



