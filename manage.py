# coding=utf-8
"""
启动命令
    python manage.py runserver -h 192.168.152.11 -p 8888
数据库操作
    python manage.py db init
    python manage.py db migrate -m 'init tables'
    python manage.py db upgrade

常见错误
1.ModuleNotFoundError: No module named 'MySQLdb'
解决：使用pymysql代替MySQLdb
2.[alembic.env] No changes in schema detected.
解决：models模块没有被工程侦测到,可以在某个模块导入models让系统知道有这么个玩意
"""

from ihome import create_app, db
from flask_script import Manager  # 命令行启动的管理类
from flask_migrate import Migrate, MigrateCommand  # 数据库迁移指令
import ihome.models

import pymysql
pymysql.install_as_MySQLdb()


# 创建flask应用对象,并指定开发/生产模式
app = create_app("develop")
# 创建启动命令管理对象,类似django的python manager.py runserver
manager = Manager(app)
# 创建数据库迁移工具对象
Migrate(app, db)
# 向启动命令管理对象中添加迁移命令
manager.add_command("db", MigrateCommand)


if __name__ == '__main__':
    # manage.py是整个工程的启动模块
    manager.run()