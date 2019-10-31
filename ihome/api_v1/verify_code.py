# coding=utf-8
"""
存放验证码的模块
Restful风格：定义后端接口的一种规范
"""
from . import api
from ihome.utils.captcha.captcha import captcha
from ihome.utils.response_code import RET
from ihome import redis_conn, constants, db
from flask import current_app, jsonify, make_response, request
from ihome.models import User
import random
from ihome.libs.yuntongxun.sms import CCP  # 发送短信验证码的接口


# 请求路径 GET http://192.168.152.11:7777/api_v1/image_code/123
@api.route('/image_code/<image_code_id>')
def get_image_code(image_code_id):
    """
    获取图片验证码
    :param image_code_id: 图片验证码的编号
    :return: 正常:返回图片验证码  异常:返回json信息
    注意：前端修改js文件后要在浏览器清除缓存,不然浏览器还会使用之前缓存的js
    """

    # 1.使用captcha库生成验证码(名称,文本值,图片数据)
    name, text, value = captcha.generate_captcha()

    # 2.将验证码文本值和编号保存到redis
    # 分析：如果用hash数据结构,"image_codes": {"id1":"aaa", "id2":"bbb"}只能整体维护"image_codes"这个key的有效期
    #      合理做法应该是单独维护每个验证码的有效期,所以选择字符串"image_code_id1": "aaa", "image_code_id2": "bbb"
    try:
        # redis操作字符串时,在设置键和值的同时可以设置有效期
        redis_conn.setex('image_code_%s' % image_code_id, constants.IMAGE_CODE_REDIS_EXPIRES, text)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg='保存图片验证码失败')

    # 返回图片数据
    response = make_response(value)
    response.headers['Content-Type'] = 'image/jpg'
    return response


# 请求路径 GET http://192.168.152.11:7777/api_v1/sms_code/<mobile>?image_code=xxxx&image_code_id=xxxx
@api.route('/sms_code/<re(r"1[3578]\d{9}"):mobile>')
def get_sms_code(mobile):
    """
    获取短信验证码
    :param mobile:
    :return:
    """

    # 1.获取参数
    image_code = request.args.get('image_code')
    image_code_id = request.args.get('image_code_id')
    # 参数校验
    if not all([image_code, image_code_id]):
        return jsonify(errno=RET.PARAMERR, errmsg='参数不完整')

    # 2.校验图片验证码
    try:
        # 从redis中取出图片验证码
        image_code_redis = redis_conn.get('image_code_%s' % image_code_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DATAERR, errmsg='redis连接异常')
    # 判断验证码是否过期
    if image_code_redis is None:
        return jsonify(errno=RET.NODATA, errmsg='验证码失效')
    # 取完就删掉防止用户多次使用同一个验证码
    try:
        redis_conn.delete('image_code_%s' % image_code_id)
    except Exception as e:
        current_app.logger.error(e)
    # 与用户填写的图片验证码比对
    if image_code.lower() != image_code_redis.lower():
        return jsonify(errno=RET.DATAERR, errmsg='验证码输入错误')

    # 3.校验手机号是否已注册
    try:
        user = User.query.filter_by(mobile=mobile).first()
    except Exception as e:
        current_app.logger.error(e)
    else:
        if user:
            return jsonify(errno=RET.DATAERR, errmsg='手机号已存在')
    # 判断该手机号60秒内是否有过操作
    try:
        flag = redis_conn.get(mobile)
    except Exception as e:
        current_app.logger.error(e)
    else:
        if flag:
            return jsonify(errno=RET.REQERR, errmsg='请求过于频繁,请稍后重试')

    # 4.未注册的话就生成短信验证码并保存
    sms_code = "%06d" % random.randint(0, 999999)
    try:
        # 将验证码保存到redis
        redis_conn.setex('sms_code_%s' % mobile, constants.SMS_CODE_REDIS_EXPIRES, sms_code)
        # 同时也保存发送给该手机号的记录,防止用户60s内再次发送发短信请求
        redis_conn.setex(mobile, constants.SEND_SMS_CODE_INTERVAL, 1)
    except Exception as e:
        current_app.logger.eror(e)
        return jsonify(errno=RET.DBERR, errmsg='保存验证码失败')

    # 5.调用接口发送短信
    try:
        ccp = CCP()
        result = ccp.send_template_sms(mobile, [sms_code, int(constants.SMS_CODE_REDIS_EXPIRES / 60)], 1)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.THIRDERR, errmsg="发送异常")
    # 返回值
    if result == 0:
        # 发送成功
        return jsonify(errno=RET.OK, errmsg="发送成功")
    else:
        return jsonify(errno=RET.THIRDERR, errmsg="发送失败")


