import os
import multiprocessing

ROOT_PATH = os.path.dirname(os.path.abspath(__file__))
LOG_PATH = "/var/log/gunicorn"

# bind = '0.0.0.0:8088'  # 绑定ip和端口号
bind = "unix:/var/run/gunicorn-socket/worker_flow.sock"
chdir = ROOT_PATH
timeout = 60  # 超时
worker_class = 'uvicorn.workers.UvicornWorker'  # 使用gevent模式，还可以使用sync 模式，默认的是sync模式
daemon = True  # 是否后台运行
debug = False
reload = False  # 每当应用程序发生更改时，都会导致工作重新启动。
workers = multiprocessing.cpu_count()  # 进程数
threads = 2  # 指定每个进程开启的线程数
loglevel = 'info'  # 日志级别，这个日志级别指的是错误日志的级别，而访问日志的级别无法设置
pidfile = "/var/run/gunicorn/worker_flow.pid"  # 存放Gunicorn进程pid的位置，便于跟踪

access_log_format = '%(t)s %(p)s %(h)s "%(r)s" %(s)s %(L)s %(b)s %(f)s" "%(a)s"'  # 设置gunicorn访问日志格式，错误日志无法设置
accesslog = os.path.join(LOG_PATH, "worker_flow-access.log")  # 访问日志文件
errorlog = os.path.join(LOG_PATH, "worker_flow-error.log")  # 错误日志文件