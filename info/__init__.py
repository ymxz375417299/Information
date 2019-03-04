# coding=utf-8
# 程序初始化启动配置

import redis

from flask import Flask, session
from flask_wtf.csrf import CSRFProtect
from flask_sqlalchemy import SQLAlchemy
from flask_session import Session
from config import Config, config

# 数据库
# 在Flask很多拓展里面都可以先实例化对象，然后再调用里init_app()方法绑定app
db = SQLAlchemy()
redis_store = None

def create_app(config_name):
    app = Flask(__name__)
    # 配置
    app.config.from_object(config[config_name])
    # 配置数据库
    db.init_app(app)
    redis_store = redis.StrictRedis(host=Config.REDIS_HOST, port=Config.REDIS_PORT)
    # 开启CSRF保护
    CSRFProtect(app)
    # 设置session保存位置，配置信息由app的config中提取，所以在config中设置session
    Session(app)
    return app






