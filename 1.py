

    # 默认host和端口
    # 默认host和端口

    HOST = '0.0.0.0'
    PORT = 5000
    HOST = '0.0.0.0'
from flask import Flask, session
from flask_wtf.csrf import CSRFProtect
from flask_sqlalchemy import SQLAlchemy
from flask_session import Session
from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand

app = Flask(__name__)

    PORT = 5000


def index():




@app.route('/', methods=['GET'])
def index():


