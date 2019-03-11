# coding=utf-8
# 程序入口
from flask import current_app
from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand
from info import create_app, db

# 创建app, 并传入配置模式：development, production, testing
app = create_app('development')


# 迁移脚本初始化，讲app和db绑定
Migrate(app, db)
# flask脚本和app绑定
manager = Manager(app)
# 把迁移命令添加到manager脚本中
manager.add_command('db', MigrateCommand)


@app.route('/', methods=['GET'])
def index():
    current_app.logger.debug('logging testing!')
    return 'hello world'


if __name__ == '__main__':
    manager.run()
