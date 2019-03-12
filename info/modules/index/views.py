# coding=utf-8
# 首页视图模块

from flask import current_app
from . import index_blu
from info import redis_store

@index_blu.route('/', methods=['GET'])
def index():
    current_app.logger.debug('logging testing!')
    redis_store.set('name', 1111111)
    return 'hello world bule'
