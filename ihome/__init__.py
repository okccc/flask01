# coding=utf-8
from flask import Flask
from config import config_map
from flask_sqlalchemy import SQLAlchemy  # 数据库
from flask_session import Session  # session
from flask_wtf import CSRFProtect  # csrf
import redis
import logging
from logging.handlers import RotatingFileHandler  # 日志记录器
from ihome.utils.commons import ReConverter  # 正则转换器


# 设置日志级别
logging.basicConfig(level=logging.DEBUG)
# 创建日志记录器,指明日志保存路径、每个日志文件的最大大小、保存的日志文件个数上限
log_handler = RotatingFileHandler("logs/log", maxBytes=1024 * 1024 * 100, backupCount=10)
# 创建日志记录格式：级别 文件:行号 信息
formatter = logging.Formatter('%(levelname)s %(filename)s:%(lineno)d %(message)s')
# 给日志记录器设置日志格式
log_handler.setFormatter(formatter)
# 为全局日志工具对象添加日志记录器
logging.getLogger().addHandler(log_handler)


# 创建数据库sqlalchemy工具对象
db = SQLAlchemy()

# 创建redis对象
redis_conn = None

# 工厂模式：定义创建对象的接口,由其子类决定实例化哪个工厂类,使创建过程延迟到子类进行
def create_app(config_type):
    # 创建flask应用对象
    app = Flask(__name__)

    # 获取配置模式类型
    config_class = config_map.get(config_type)
    app.config.from_object(config_class)

    # 初始化db,将db绑定到app
    db.init_app(app)

    # 初始化redis工具
    global redis_conn
    redis_conn = redis.StrictRedis(host=config_class.REDIS_HOST, port=config_class.REDIS_PORT)

    # 将session数据保存到redis中
    Session(app)

    # 为flask对象补充csrf防护
    CSRFProtect(app)

    # 将自定义转换器添加到app
    app.url_map.converters['re'] = ReConverter

    # 注册蓝图到app,使用时再import防止循环导入
    from ihome.api_1 import api
    app.register_blueprint(api, url_prefix="/api_1")
    from ihome.index import html  # 访问静态文件的蓝图
    app.register_blueprint(html)

    return app