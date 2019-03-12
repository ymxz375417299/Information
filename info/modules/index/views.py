# coding=utf-8
# 首页视图模块

from . import index_blu
from info import redis_store
from flask import current_app, render_template


@index_blu.route('/', methods=['GET'])
def index():
    """首页"""
    current_app.logger.debug('logging testing!')
    redis_store.set('name', 1111111)
    return render_template('news/index.html')


@index_blu.route('/favicon.ico')
def favicon():
    """网站图标"""
    # send_static_file是flask里面的寻找static静态文件的方法。通过查看源码得知
    return current_app.send_static_file('news/favicon.ico') 
