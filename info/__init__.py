# coding=utf-8
# 程序初始化启动配置

import redis

from flask import Flask, session
from flask_wtf.csrf import CSRFProtect
from flask_sqlalchemy import SQLAlchemy
from flask_session import Session
from config import Config

app = Flask(__name__)

app.config.from_object(Config)
db = SQLAlchemy(app)
redis_store = redis.StrictRedis(host=Config.REDIS_HOST, port=Config.REDIS_PORT)
CSRFProtect(app)
# 设置session保存位置，配置信息由app的config中提取，所以在config中设置session
Session(app)


