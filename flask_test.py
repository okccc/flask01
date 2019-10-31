# coding=utf-8
import unittest
from flask01 import app
import json


class TestLogin(unittest.TestCase):
    """编写测试用例"""
    def setUp(self):
        """setUp方法在执行具体的测试方法前会被调用,相当于__init__"""
        # 激活测试标志,显示所有bug
        app.config['DEBUG'] = True
        # 使用flask提供的测试客户端测试
        self.client = app.test_client()

    def test_login_name_password(self):
        # 模拟post请求,data指定发生数据
        # response = self.client.post('/login', data={"name": "grubby"})
        response = self.client.post('/login', data={"name": "grubby", "password": "orc"})
        print(response.data)
        # 解析响应数据
        dict_data = json.loads(response.data)
        # 使用断言
        self.assertIn('code', dict_data)
        # 校验断言结果
        code = dict_data['code']
        # 继续使用断言
        self.assertEquals(code, 0)


if __name__ == '__main__':
    # 启动测试
    unittest.main()

