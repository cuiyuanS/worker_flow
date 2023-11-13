## 工作流 worker_flow

### 环境要求
- Python 3.8+
- MongoDB 5.0

### 环境布署
- 进入当前项目目录  
- 创建虚拟环境(只在第一次布署时创建 < 3.6)：```virtualenv env```  
- 创建虚拟环境(只在第一次布署时创建 >= 3.6)：```python3 -m venv env``` 
- 切换到虚拟环境：```source env/bin/activate```  
- 安装依赖: ```pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple```   

### 首次配置
- 把根目录文件```config_example.ini```复制到根目录```config.ini```，作为当前环境的配置文件  
- 把根目录文件```.gitignore_example```复制到根目录```.gitignore```，作为当前项目的git忽略文件  
- 把根目录文件```gunicorn_example.py```复制到根目录```gunicorn.py```，作为当前项目的gunicorn配置文件 

### 开发环境启动
- 切换当前虚拟环境: ```source env/bin/activate``` 
- 浏览地址：``` http://127.0.0.1:8200 ```  

### 启动程序uwsgi:
- 切换当前虚拟环境: ```source env/bin/activate``` 
- 首次创建 gunicorn 日志文件并给写权限:
```
sudo touch /var/log/gunicorn/worker_flow.log
sudo chmod 777 /var/log/gunicorn/worker_flow.log
```
- 首次创建 gunicorn socket文件夹并修改组和用户名为当前用户
```
sudo mkdir /var/run/gunicorn-socket
sudo chown -R mei:mei /var/run/gunicorn-socket/
```
- 首次创建 gunicorn pid文件并给写权限:
```
sudo mkdir /var/run/gunicorn
sudo chown -R mei:mei /var/run/gunicorn/
sudo touch /var/run/gunicorn/worker_flow.pid
```
- 启动uwsgi服务器: ```gunicorn  manage:app -c gunicorn.py```  
- 快捷启动脚本: ```bash deploy.sh start|stop|restart```  

### 退出当前虚拟环境
```
deactivate
``` 

