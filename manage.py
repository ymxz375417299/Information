# coding=utf-8
# 程序入口

import redis

from flask import Flask, session
from flask_wtf.csrf import CSRFProtect
from flask_sqlalchemy import SQLAlchemy
from flask_session import Session
from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand
from config import Config

app = Flask(__name__)





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
