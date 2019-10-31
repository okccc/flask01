# coding=utf-8
from flask import Blueprint, current_app, make_response  # current_app代表当前app
from flask_wtf import csrf

# 提供首页静态文件的蓝图
html = Blueprint('html', __name__)

# 192.168.152.11:8888/
# 192.168.152.11:8888/index.html
# 192.168.152.11:8888/register.html
# 192.168.152.11:8888/favicon.ico   # 浏览器认为的网站标识,浏览器会自己请求这个资源

@html.route("/<re(r'.*'):filename>")
def get_index(filename):
    # 判断请求路径
    if not filename:
        filename = "html/index.html"
    # if filename != "favicon.ico":
    else:
        filename = "html/" + filename + ".html"
    # 创建csrftoken值
    csrf_token = csrf.generate_csrf()
    # 使用发送静态文件的内部功能
    response = make_response(current_app.send_static_file(filename))
    # 往cookie添加csrf_token值
    response.set_cookie('csrf', csrf_token)
    # 返回响应
    return response



