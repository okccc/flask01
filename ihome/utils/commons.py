# coding=utf-8
"""
该模块保存常用工具包
"""
from werkzeug.routing import BaseConverter  # 转换器基类
import functools
from flask import session, jsonify, g
from ihome.utils.response_code import RET

class ReConverter(BaseConverter):
    """自定义正则转换器类"""
    def __init__(self, url_map, regex):
        # 调用父类初始化方法
        super(ReConverter, self).__init__(url_map)
        # 将正则表达式作为参数保存到对象的属性中
        self.regex = regex


def login_required(view_func):
    """登录装饰器"""
    # wraps函数的作用是将wrapper内层函数的属性设置为被装饰函数view_func的属性
    @functools.wraps(view_func)
    def wrapper(*args, **kwargs):
        # 判断用户的登录状态
        user_id = session.get("user_id")
        if user_id:
            # 将user_id保存到g对象中,在视图函数中可以通过g对象获取保存数据
            g.user_id = user_id
            # 如果已登录就执行视图函数
            return view_func(*args, **kwargs)
        else:
            # 如果未登录就返回错误信息
            return jsonify(errno=RET.SESSIONERR, errmsg="用户未登录")

    return wrapper

