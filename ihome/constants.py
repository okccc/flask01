# coding=utf-8
"""
该模块保存工程中使用的常量值
"""

# 图片验证码的redis有效期
IMAGE_CODE_REDIS_EXPIRES = 180

# 短信验证码的redis有效期
SMS_CODE_REDIS_EXPIRES = 300

# 发送短信验证码的时间间隔
SEND_SMS_CODE_INTERVAL = 60