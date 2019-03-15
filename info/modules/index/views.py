# coding=utf-8
# 首页视图模块

from . import index_blu
from info import redis_store
from info.models import User
from flask import current_app, render_template
from flask import session


@index_blu.route('/', methods=['GET'])
def index():
    """
    首页
    1. 如果用户已经登录，将当前登录用户的数据传到模板，供模板显示
    """
    # 获取当前登录的用户id(来自session)默认值为空
    user_id = session.get('user_id', '')
    # 通过id获取用户信息
    user = None
    if user_id:
        # 尝试查询用户的模型
        try:
            user = User.query.get(user_id)
        except Exception as e:
            current_app.logger.error(e)
    data = {
        "user_info": user.to_dict() if user else None # 有值取值
        # to_dict是flask的user模型的提供一个方法，把属性转成字典
            }
            
    return render_template('news/index.html', data=data)


@index_blu.route('/favicon.ico')
def favicon():
    """网站图标"""
    # send_static_file是flask里面的寻找static静态文件的方法。通过查看源码得知
    return current_app.send_static_file('news/favicon.ico') 
