# coding=utf-8
from . import api
from flask import g, current_app, jsonify, request
from ihome.utils.response_code import RET
from ihome.models import Area
from ihome import constants, redis_conn
import json


@api.route("/areas")
def get_area_info():
    """获取城区信息"""
    try:
        # 1.先尝试从redis中读取数据
        area_info = redis_conn.get("area_info")
    except Exception as e:
        current_app.logger.error(e)
    else:
        if area_info:
            # redis有缓存数据
            current_app.logger.info("hit redis area_info")
            # Content-Type默认是text/html
            return area_info, 200, {"Content-Type": "application/json"}

    try:
        # 2.redis没有数据再去查询数据库
        area_li = Area.query.all()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="数据库异常")

    areas = []
    # 将对象转换为字典
    for area in area_li:
        areas.append(area.to_dict())
    area_info = json.dumps(dict(areas))

    try:
        # 3.将mysql查询数据保存到redis中
        redis_conn.setex("area_info", constants.AREA_INFO_REDIS_CACHE_EXPIRES, area_info)
    except Exception as e:
        current_app.logger.error(e)

    return area_info, 200, {"Content-Type": "application/json"}