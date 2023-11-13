from copy import copy
import importlib

from src.worker.gearman_sync_help.worker import Worker
from src.worker.task_status import TaskStatus
from src.worker.worker_run_error import *
from src.worker.worker_sync_log import get_worker_client_handler, remove_logger_handler


def import_and_new_class(class_name:str):
    """
    动态导入 worker 功能函数
    :param class_name: 任务名称
    :return: 任务类
    """
    # 如果在您的程序运行时创建/安装了任何模块，则应调用此函数，以确保所有发现者都会注意到新模块的存在。
    importlib.invalidate_caches()
    _module = importlib.import_module("src.worker.worker_register_func.%s" % class_name)
    return getattr(_module, class_name)


def exe_func(class_name, gearman_worker, gearman_job, logger):
    """
    worker 执行
    :param class_name: 任务类名
    :param gearman_worker: gearman worker
    :param gearman_job: gearman job
    :param logger: 日志logger
    :return:
    """
    try:
        t = import_and_new_class(class_name)
    except Exception as e:
        raise WorkerNotFound(class_name, str(e))
    o: Worker = t(gearman_worker, gearman_job, logger)
    return o._run()


class TaskObj:
    def __init__(self, worker_server, server_info):
        """
        :param worker_server: worker_server 类
        :param server_info: 服务信息
        """
        self.class_name = server_info["cla_name"]
        self.server_info = server_info
        self.worker_server = worker_server
        self.logger = None

    def task_func(self, gearman_worker, gearman_job):
        try:
            self.logger = get_worker_client_handler(gearman_worker.worker_client_id)
        except Exception as e:
            raise LogGetError(str(e))
        data = gearman_job.data
        worker_id = copy(gearman_worker.worker_client_id)
        message = ""
        code = TaskStatus.SUCCESS.value
        res_data = {}
        try:
            res = exe_func(self.class_name, gearman_worker, gearman_job, self.logger)
            if res["code"] == TaskStatus.SUCCESS.value:
                res_data = res["data"]
            else:
                message = res["message"]
                code = res["code"]
                self.logger.error(f"{self.class_name} 运行错误 {message}")
        except Exception as e:
            code = TaskStatus.WORKER_FAIL.value
            message = str(e)
        finally:
            self.remove_logger()
        result = {"data": res_data,  # 任务结果 如果失败的话 是错误信息
                  "message": message,
                  "code": code,
                  "from_params": data,  # 执行这个任务 所使用的参数
                  "server": self.server_info["host"],  # 执行这个任务的 服务器名
                  "worker_id": worker_id}  # 执行这个任务的 worker_id
        return result

    def remove_logger(self):
        remove_logger_handler(self.logger)
