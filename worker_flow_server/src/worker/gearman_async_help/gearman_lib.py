import importlib
import traceback

from src.helper.logs import worker_async_logger
from src.worker.common import post_json
from src.worker.worker_error import WorkerSerializeError


def import_and_new_class(class_name: str):
    """
    动态导入 worker 功能函数
    :param class_name: 任务名称
    :return: 任务类
    """
    # 如果在您的程序运行时创建/安装了任何模块，则应调用此函数，以确保所有发现者都会注意到新模块的存在。
    importlib.invalidate_caches()
    _module = importlib.import_module("src.worker.worker_async.%s" % class_name)
    return getattr(_module, class_name)


def exe_func(class_name, gearman_worker, gearman_job):
    """
    worker 执行
    :param class_name: 任务类名
    :param gearman_worker: gearman worker
    :param gearman_job: gearman job
    :return:
    """

    t = import_and_new_class(class_name)
    try:
        a = t(gearman_worker, gearman_job)
    except WorkerSerializeError as e:
        return

    return a._run()


class TaskObj:
    def __init__(self, class_name):
        """
        :param class_name: class_name
        """
        self.class_name = class_name

    def task_func(self, gearman_worker, gearman_job):
        try:
            userdata = gearman_job.data.get("userdata", None)
            callback_url = gearman_job.data.get("callback_url", None)
            if userdata and callback_url:
                res = exe_func(self.class_name, gearman_worker, gearman_job)
                res["userdata"] = userdata
                print("回调参数", res)
                print("回调url", callback_url)
                # {'code': 603, 'message': '任务处理失败 项目标记 2DC3D_Flame_FFHQ 异常消息 客户端提交job失败：任务名称为 AIGenModelFlameFFHQWorker 的 worker 未找到', 'userdata': {'11': 11}}
                callback_response = post_json(callback_url, json=res)
                if not callback_response["success"]:
                    worker_async_logger.warning(f'api 回调请求失败 {callback_response["message"]}')
            else:
                worker_async_logger.warning("sync_worker_server 异常 不构成回调 不执行")
        except Exception as e:
            worker_async_logger.exception("sync_worker_server 异常： "+ str(e))
