# config=utf-8
from flask import Blueprint

index_blu = Blueprint('index', __name__)

# 导入视图模块
from . import views

