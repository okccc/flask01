# coding=utf-8
from flask import Blueprint


# 创建蓝图对象,api_1是蓝图名称,__name__表示蓝图所在模块
api = Blueprint("api_v1", __name__)

# 请求路径 http://192.168.152.11:7777/api_1/test
@api.route('/test')
def test():
    return 'it is test'

# 导入该蓝图的视图函数,先创建蓝图再import防止循环导入
from . import verify_code

