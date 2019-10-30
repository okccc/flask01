# coding=utf-8
from . import api
from ihome import redis_conn, db, constants
from flask import request, jsonify, current_app, session
from ihome.utils.response_code import RET
from ihome.models import User
from sqlalchemy.exc import IntegrityError  # 数据库异常,mobile字段设置了unique=True,多次插入会报这个错
import re


@api.route('/users', methods=['POST'])
def register():
    """
    注册
    请求参数：手机号、短信验证码、密码、确认密码
    参数格式：json
    :return:
    """

    # 接收参数
    req_dict = request.get_json()
    mobile = req_dict.get('mobile')
    sms_code = req_dict.get('sms_code')
    password = req_dict.get('password')
    password2 = req_dict.get('password2')

    # 校验参数完整性
    if not all([mobile, sms_code, password, password2]):
        return jsonify(errno=RET.PARAMERR, errmsg='参数不完整')

    # 判断手机号格式
    if not re.match(r"1[34578]\d{9}", mobile):
        return jsonify(errno=RET.PARAMERR, errmsg="手机号格式错误")

    # 判断密码
    if password != password2:
        return jsonify(errno=RET.PARAMERR, errmsg="两次密码不一致")

    # 从redis中取出短信验证码
    try:
        sms_code_redis = redis_conn.get("sms_code_%s" % mobile)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="读取短信验证码异常")

    # 判断短信验证码是否过期
    if sms_code_redis is None:
        return jsonify(errno=RET.NODATA, errmsg="短信验证码失效")

    # 删除redis中的短信验证码,防止重复使用校验
    try:
        redis_conn.delete("sms_code_%s" % mobile)
    except Exception as e:
        current_app.logger.error(e)

    # 判断用户填写短信验证码的正确性
    if sms_code_redis != sms_code:
        return jsonify(errno=RET.DATAERR, errmsg="短信验证码错误")

    # 将新注册用户保存到数据库
    user = User(name=mobile, mobile=mobile)
    # 设置属性
    user.password = password
    try:
        db.session.add(user)
        db.session.commit()
    except IntegrityError as e:
        # 数据库操作错误后要回滚
        db.session.rollback()
        # mobile字段出现重复值,表示该手机号已经注册过
        current_app.logger.error(e)
        return jsonify(errno=RET.DATAEXIST, errmsg="手机号已存在")
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="数据库操作异常")

    # 保存登录状态到session中
    session["name"] = mobile
    session["mobile"] = mobile
    session["user_id"] = user.id

    # 返回结果
    return jsonify(errno=RET.OK, errmsg="注册成功")


@api.route('/sessions', methods=['POST'])
def login():
    """
    登录
    请求参数：手机号、密码
    参数格式：json
    :return:
    """

    # 接收参数
    req_dict = request.get_json()
    mobile = req_dict.get('mobile')
    password = req_dict.get('password')

    # 校验参数完整性
    if not all([mobile, password]):
        return jsonify(errno=RET.PARAMERR, errmsg='参数不完整')

    # 判断手机号格式
    if not re.match(r"1[34578]\d{9}", mobile):
        return jsonify(errno=RET.PARAMERR, errmsg="手机号格式错误")

    # 判断错误次数是否超过限制
    user_ip = request.remote_addr  # 用户的ip地址
    try:
        # redis记录： "access_nums_请求的ip": "次数"
        access_nums = redis_conn.get("access_num_%s" % user_ip)
    except Exception as e:
        current_app.logger.error(e)
    else:
        if access_nums and int(access_nums) >= constants.LOGIN_ERROR_MAX_TIMES:
            return jsonify(errno=RET.REQERR, errmsg="错误次数过多,请稍后重试")

    # 查询用户信息
    try:
        user = User.query.filter_by(mobile=mobile).first()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="获取用户信息失败")

    # 密码比对
    if user is None or not user.check_password(password):
        try:
            # 验证失败时记录错误次数：redis的incr方法可以对字符串类型的数字数据进行加一操作,如果数据一开始不存在,则会初始化为1
            redis_conn.incr("access_num_%s" % user_ip)
            # 设置登录错误限制时间
            redis_conn.expire("access_num_%s" % user_ip, constants.LOGIN_ERROR_FORBID_TIME)
        except Exception as e:
            current_app.logger.error(e)
        return jsonify(errno=RET.DATAERR, errmsg="用户名或密码错误")

    # 保存登录状态到session中
    session["name"] = user.name
    session["mobile"] = user.mobile
    session["user_id"] = user.id

    # 返回结果
    return jsonify(errno=RET.OK, errmsg="登录成功")


@api.route("/session", methods=["GET"])
def check_login():
    """检查登陆状态"""
    # 从session中获取用户名
    name = session.get("name")
    # 判断是否已登录
    if name:
        return jsonify(errno=RET.OK, errmsg="true", data={"name": name})
    else:
        return jsonify(errno=RET.SESSIONERR, errmsg="false")


@api.route("/session", methods=["DELETE"])
def logout():
    """退出"""
    # 清除session数据
    session.clear()
    return jsonify(errno=RET.OK, errmsg="OK")