from flask import Flask, request, redirect, url_for
from werkzeug.routing import BaseConverter

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

# 定义路由,methods限定请求方式
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
    # 接收文件
    file = request.files.get('pic')
    if file:
        file.save('demo.jpg')
    return 'hello name=%s, names=%s, data=%s, city=%s' % (name, names, data, city)

@app.route('/login')
def login():
    # url_for通过视图名称找到对应路由
    url = url_for('index')
    # 重定向
    return redirect(url)


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


if __name__ == '__main__':
    # url_map查看整个flask路由信息
    print(app.url_map)
    # 启动flask程序
    app.run(host='192.168.152.11', port=5000, debug=True)  # host='0.0.0.0'表示允许任何ip访问,开启debug显示错误信息
