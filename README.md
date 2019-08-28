#### gunicorn启动命令
- gunicorn -w 4 -b 192.168.152.11:5000 -D --access-logfile log/err.log flask01:app  
-w：进程数  
-b：绑定地址:端口  
-D：守护进程  
--access-logfile：指定日志文件  
flask01:app：运行文件名称:flask应用程序

#### 修改nginx配置文件
```
#gzip  on;
upstream flask{
    # flask集群地址,nginx要单独装一台机器,外界通过nginx访问网站
    server 192.168.152.11:5000;
    server 192.168.152.11:5001;
}

server {
    listen       80;
    server_name  localhost;

    #charset koi8-r;
    #access_log  logs/host.access.log  main;

    location / {
        # nginx会做负载均衡,将请求轮询分发到flask集群
        proxy_pass http://flask;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
```

#### 启动nginx
- /usr/local/nginx/sbin/nginx
- 通过浏览器访问  http://192.168.152.12

