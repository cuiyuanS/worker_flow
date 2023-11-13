import sys
import traceback

from src.worker.gearman_sync_help.worker_handle import WorkerServer
try:
    import systemd.daemon
except:
    systemd = None


def run():
    worker_server = WorkerServer()
    # 开启一个线程 动态获取配置文件 更新 注册 worker
    try:
        worker_server.start()
    except:
        print(traceback.print_exc())
        sys.exit(235)  # 异常 systemctl 会重试
    finally:
        worker_server.stop()


if __name__ == '__main__':
    if systemd:
        systemd.daemon.notify('READY=1')
    run()
