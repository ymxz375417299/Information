# coding=utf-8
# 程序初始化启动配置

import redis
import logging
from logging.handlers import RotatingFileHandler

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
    """返回app"""
    # 日志模块
    setup_log(config_name)
    app = Flask(__name__)
    # 配置
    app.config.from_object(config[config_name])
    # 配置数据库
    db.init_app(app)
    global redis_store
    redis_store = redis.StrictRedis(
        host=Config.REDIS_HOST, port=Config.REDIS_PORT)
    # 开启CSRF保护
    CSRFProtect(app)
    # 设置session保存位置，配置信息由app的config中提取，所以在config中设置session
    Session(app)
    # 注册首页模块蓝图
    from info.modules.index import index_blu
    app.register_blueprint(index_blu)
    # 注册passport模块蓝图
    from info.modules.passport import passport_blu 
    app.register_blueprint(passport_blu)

    return app


def setup_log(config_name):
    """配置日志"""
    # 设置日志的登记
    logging.basicConfig(level=config[config_name].LOG_EVEL)
    # 创建日志记录器
    # 指明日志保存路径，每个日志文件的最大大小，保存的日志文件个数上线
    file_log_handler = RotatingFileHandler(
        'logs/log', maxBytes=1024*1024*100, backupCount=10)
    # 创建日志记录的格式，日志等级，输入日志信息的文件夹名，行书，日志信息
    formatter = logging.Formatter(
        '%(levelname)s %(filename)s lines: %(lineno)d massage: %(message)s')
    # 为刚创建的日志记录器设置日志记录格式
    file_log_handler.setFormatter(formatter)
    # 为全局日志工具对象（flaskk app 使用）添加日志记录器
    logging.getLogger().addHandler(file_log_handler)
