# coding=utf-8
from flask import Flask, request, redirect, url_for, abort, Response, make_response, jsonify, session, render_template
from werkzeug.routing import BaseConverter  # 转换器类
from flask_script import Manager  # 命令行启动的管理类

# 创建flask应用对象
app = Flask(
    # __name__使用说明：如果是程序运行入口就是__main__,如果是被当做模块导入就是模块名
    __name__,  # __name__表示当前模块名字,flask以这个模块所在目录为根目录,根目录中的static为静态目录,templates为模板目录
    static_url_path='/flask',  # 设置访问静态资源的url前缀,默认static
    static_folder='static',  # 存放静态文件的目录,默认static
    template_folder='templates',  # 存放模板文件的目录,默认templates
)

# 参数配置方式
# 1.使用配置文件
# app.config.from_pyfile('config.cfg')
# 2.使用对象配置参数
class Config(object):
    DEBUG = True
app.config.from_object(Config)
# 3.直接操作config字典对象
# app.config['DEBUG'] = True

# 定义路由,methods限定请求方式,默认GET
@app.route('/', methods=['GET', 'POST'])
# 定义视图函数
def index():
    # request对象包含前端发送过来的所有请求数据
    # 提取表单数据
    name = request.form.get('name')
    names = request.form.getlist('name')
    # 提取非表单数据(比如json)
    data = request.data
    # 提取url中的参数
    city = request.args.get('city')
    # return 'hello name=%s, names=%s, data=%s, city=%s' % (name, names, data, city)
    # 接收文件
    file = request.files.get('pic')
    if file:
        file.save('demo.jpg')
    # 构造响应信息
    # response = make_response('hello')  # 响应体
    # response.status = '200 ok'  # 状态码
    # response.headers['city'] = 'shanghai'  # 响应头
    # return response
    data = {
        'name': 'grubby',
        'age': 18
    }
    # jsonify将字典转换成json数据返回,并设置响应头Content-Type: application/json,不然是Content-Type: text/html; charset=utf-8
    return jsonify(data)  # 类似django的JsonResponse
    # 获取session信息
    # username = session.get('username')
    # age = session.get('age')
    # return 'hello %s, %d' % (username, age)


@app.route('/login')
def login():
    name, pwd = '', ''
    if name == 'grubby' and pwd == 'orc':
        # url_for通过视图名称找到对应路由
        url = url_for('index')
        return redirect(url)
    else:
        # abort函数：传递状态码或响应体,终止视图函数执行并给前端返回特定信息
        abort(404)
        # abort(Response('login failed!'))

# 自定义错误处理方法
@app.errorhandler(404)
def handle_404(err):
    # 给前端响应错误处理信息
    return '当前页面请求错误, %s' % err

# 默认转换器：路由传递的参数默认字符串,可使用int/float转换器
# @app.route('/goods/<goods_id>')
@app.route('/goods/<int:goods_id>')
def goods(goods_id):
    return 'goods is %s' % goods_id

# 自定义转换器
class RegexConverter(BaseConverter):
    def __init__(self, url_map, regex):
        # 调用父类初始化方法
        super(RegexConverter, self).__init__(url_map)
        # 将正则作为参数保存到对象的属性中,flask会使用这个属性对路由做正则匹配
        self.regex = regex

    def to_python(self, value):
        # value是在对路由做正则匹配时提取的参数
        return value

    def to_url(self, value):
        """使用url_for方法时被调用"""
        return value

# 将自定义转换器re添加到app
app.url_map.converters['re'] = RegexConverter

@app.route('/send/<re(r"1[34578]\d{9}"):mobile>')
def send(mobile):
    return 'send msg to %s' % mobile

@app.route('/cookie01')
def cookie01():
    response = make_response('cookie测试')
    # 设置cookie：浏览器地址栏左侧感叹号 - 查看网站信息 - 查看cookie使用情况
    response.set_cookie(key='k1', value='v1', max_age=3600)
    # 删除cookie：浏览器并没有立即删除该cookie,而是设置到期时间=创建时间表示该cookie已失效,浏览器本身会定时清理网站cookie信息
    response.delete_cookie(key='k1')
    return response

# flask中session需使用秘钥字符串
app.config['SECRET_KEY'] = 'adasfasfe2ssdfefsf'  # 随机字符串
@app.route('/session01')
def session01():
    # flask默认把session信息和秘钥字符串糅杂在一起保存到cookie中,django是保存到后端数据库mysql/redis
    session['username'] = 'grubby'
    session['age'] = 18
    return 'session测试'

# flask中的钩子函数相当于django中的中间件
@app.before_first_request
def before_first_request():
    # 处理第一个请求之前被执行
    print('before_first_request 被执行')

@app.before_request
def before_request():
    # 每次请求之前都被执行
    print('before_request 被执行')

@app.after_request
def after_request(response):
    # 每次请求视图函数之后都被执行,前提是不出现异常
    print('after_request 被执行')
    return response

@app.teardown_request
def teardown_request(response):
    # 每次请求视图函数之后都被执行,无论是否出现异常,但是要在非调试模式下debug=False
    print('teardown_request 被执行')
    return response

# 将app交给manager管理,类似django的python manager.py runserver ip:port
manager = Manager(app)

# jinja2模板
@app.route('/template')
def template():
    data = {
        "name": "grubby",
        "age": 18,
        "my_dict": {"city": "上海"},
    }
    # 渲染模板,**data表示将字典拆包成key=value对
    return render_template('index.html', **data)




if __name__ == '__main__':
    # 查看flask应用所有路由信息
    print(app.url_map)
    # 启动flask程序
    app.run(host='192.168.152.11', port=5000, debug=True)  # host='0.0.0.0'表示允许任何ip访问,开启debug显示错误信息
    # 通过manager启动flask,在终端输入命令行python flask01.py runserver -h 192.168.152.11 -p 8888
    # manager.run()
