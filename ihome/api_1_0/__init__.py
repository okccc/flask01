# coding=utf-8
from flask import Blueprint

# 创建蓝图对象,api_1_0是蓝图名称,__name__表示蓝图所在模块
api = Blueprint("api_1_0", __name__)

@api.route('/index')
def index():
    return 'it is test'


