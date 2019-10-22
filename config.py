# coding=utf-8
import redis


class Config(object):
    """全局配置信息"""

    # 字符串秘钥
    SECRET_KEY = "XHSOI*Y9dfs9cshd9"

    # sqlalchemy的配置参数
    SQLALCHEMY_DATABASE_URI = "mysql://root:root@192.168.152.11:3306/flask"
    # 设置sqlalchemy自动更跟踪数据库
    SQLALCHEMY_TRACK_MODIFICATIONS = True

    # redis
    REDIS_HOST = '192.168.152.11'
    REDIS_PORT = 6379

    # flask-session
    SESSION_TYPE = "redis"  # session存到redis
    SESSION_REDIS = redis.StrictRedis(host=REDIS_HOST, port=REDIS_PORT)  # 连接redis
    SESSION_USE_SIGNER = True  # 对cookie中session_id进行隐藏处理
    PERMANENT_SESSION_LIFETIME = 86400  # session生命周期


class DevelopConfig(Config):
    """开发环境"""
    DEBUG = True


class ProductConfig(Config):
    """生产环境"""
    pass


config_map = {
    "develop": DevelopConfig,
    "product": ProductConfig
}