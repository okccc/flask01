# coding=utf-8
"""
常用工具包
"""
from werkzeug.routing import BaseConverter  # 转换器基类

class ReConverter(BaseConverter):
    """自定义正则转换器类"""
    def __init__(self, url_map, regex):
        # 调用父类初始化方法
        super(ReConverter, self).__init__(url_map)
        # 将正则表达式作为参数保存到对象的属性中
        self.regex = regex

