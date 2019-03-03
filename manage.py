# coding=utf-8
# 程序入口

import redis

from flask import Flask, session
from flask_wtf.csrf import CSRFProtect
from flask_sqlalchemy import SQLAlchemy
from flask_session import Session
from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand

app = Flask(__name__)

class Config:
    """工程配置信息"""
    DEBUG = True
    # # 默认host和端口
    # HOST = '0.0.0.0'
    # PORT = 5000
    # mysql配置
    SQLALCHEMY_DATABASE_URI = 'mysql://root:mysql@127.0.0.1:3306/information'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    # redis配置
    REDIS_HOST = '127.0.0.1'
    REDIS_PORT = 6379
    # 安全秘钥
    SECRET_KEY = 'RFIAGD3GEemj+qx7oUa2IERSABk9xhHpnmGse6FGtiA='
    SESSION_TYPE = 'redis' # session保存到redis
    SESSION_REDIS = redis.StrictRedis(host=REDIS_HOST, port=REDIS_PORT) # 使用自己导入的redis的实例，默认会自己帮我们传，但是会把端口配置固定，不够灵活
    SESSION_USE_SIGNER = True # 让cookie中的session_id 被加密签名处理
    SESSION_PERMANENT = False # 设置session过期
    PERMANENT_SESSION_LIFETIME = 86400 * 2 # session的有效期2天，单位秒，默认31天




app.config.from_object(Config)
db = SQLAlchemy(app)
redis_store = redis.StrictRedis(host=Config.REDIS_HOST, port=Config.REDIS_PORT)
CSRFProtect(app)
# 设置session保存位置，配置信息由app的config中提取，所以在config中设置session
Session(app)
# 迁移脚本初始化，讲app和db绑定
Migrate(app, db)
# flask脚本和app绑定
manager = Manager(app)
# 把迁移命令添加到manager脚本中
manager.add_command('db', MigrateCommand)


@app.route('/', methods=['GET'])
def index():
    session['test'] = 'abcdsadsad' # 测试session
    return 'hello world'


if __name__ == '__main__':
    manager.run()
