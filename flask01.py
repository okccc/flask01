from flask import Flask

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

@app.route('/')
def index():
    # 获取配置参数
    # a = 1/0
    print(app.config.get('DEBUG'))
    return 'hello flask!'


if __name__ == '__main__':
    # 启动flask程序
    app.run(host='192.168.152.11', port=5000, debug=True)  # host='0.0.0.0'表示允许任何ip访问,开启debug显示错误信息
