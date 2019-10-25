# coding=utf-8
"""
存放验证码的模块
Restful风格：定义后端接口的一种规范
"""
from . import api
from ihome.utils.captcha.captcha import captcha
from ihome.utils.response_code import RET
from ihome import redis_conn, constants
from flask import current_app, jsonify, make_response

# 请求路径 http://192.168.152.11:7777/api_1/image_code/123
@api.route('/image_code/<image_code_id>')
def get_image_code(image_code_id):
    """
    获取图片验证码
    :param image_code_id: 图片验证码的编号
    :return: 正常:返回验证码图片  异常:返回json信息
    """

    # 使用captcha库生成验证码(名称,文本值,图片数据)
    name, text, value = captcha.generate_captcha()
    # 将验证码文本值和编号保存到redis
    # 分析：如果用hash数据结构,"image_codes": {"id1":"aaa", "id2":"bbb"}只能整体维护"image_codes"这个key的有效期
    #      合理做法应该是单独维护每个验证码的有效期,所以选择字符串"image_code_id1": "aaa", "image_code_id2": "bbb"
    try:
        # redis操作字符串时,在设置键和值的同时可以设置有效期
        redis_conn.setex(image_code_id, constants.IMAGE_CODE_REDIS_EXPIRES, text)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg='保存图片验证码失败')

    # 返回图片数据
    response = make_response(value)
    response.headers['Content-Type'] = 'image/jpg'
    return response
