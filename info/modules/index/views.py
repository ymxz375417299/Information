# coding=utf-8
# 首页视图模块

from flask import current_app
from . import index_blu

@index_blu.route('/', methods=['GET'])
def index():
    current_app.logger.debug('logging testing!')
    return 'hello world bule'
