import multiprocessing
import sys
import os
import time

from src.config.worker import ASYNC_JOB_ADDRESS
from src.worker.gearman_help.util import GearmanJsonWorker
from src.worker.gearman_async_help.gearman_lib import TaskObj
from src.lib.gearman.errors import ServerUnavailable


class WorkerServer:
    """
    根据配置 注册并管理 多线程 worker
    """

    def __init__(self):
        self.worker_config = {}
        self.threads_id = 0
        self.pool = None
        self.get_worker_config()

    @staticmethod
    def get_modules(package="src/worker/worker_async"):
        """
        获取包名下所有非__init__的模块名
        """
        modules = {}
        files = os.listdir(package)

        # exclude = ["SDImageToImage"]
        exclude = []

        for file in files:
            if not file.startswith("__"):
                name, ext = os.path.splitext(file)
                if name in exclude:
                    continue
                modules[name] = 1

        return modules

    def get_worker_config(self):
        self.worker_config = self.get_modules()

    def get_threads_id(self):
        self.threads_id += 1
        return self.threads_id

    def register_task(self, task_name, func, job_address_list=["127.0.0.1:4730"]):
        """
        注册任务
        :param job_address_list: job ip 地址
        :param task_name: 任务名
        :param func: 函数名
        :return:
        """
        if not job_address_list:
            return
        # worker 注册 task 一个 task  多个 worker
        gm_worker = GearmanJsonWorker(job_address_list)
        client_id = "worker_" + task_name + "_" + str(self.get_threads_id())
        gm_worker.set_client_id(client_id)
        gm_worker.register_task(("async_queue_"+task_name).encode("utf-8"), func)
        try:
            gm_worker.work()
        except ServerUnavailable:
            gm_worker.unregister_task(("async_queue_"+task_name).encode("utf-8"))
            time.sleep(5)
            self.register_task(("async_queue_"+task_name).encode("utf-8"), func, job_address_list)

    def update_workers(self):
        worker_num = 0
        for task_name, t_nun in self.worker_config.items():
            worker_num += t_nun
        if not worker_num:
            return
        self.pool = multiprocessing.Pool(processes=worker_num)
        for task_name, t_nun in self.worker_config.items():
            for n in range(t_nun):
                args = (task_name, TaskObj(task_name).task_func, ASYNC_JOB_ADDRESS)
                self.pool.apply_async(func=self.register_task, args=args, error_callback=self.pool_exception)
        try:
            self.pool.close()
            self.pool.join()
        except KeyboardInterrupt:
            return

    def pool_exception(self, exception):
        print(exception)

    def stop(self):
        # 停止所有worker
        if self.pool:
            self.pool.terminate()
            self.pool.join()
        # if hasattr(self, "workers") and self.workers:
        sys.exit(0)

    def start(self):
        # 开始 挂起worker
        # try:
        #     signal.signal(signal.SIGTERM, self.stop)
        # except Exception as e:
        #     self.logger.error(traceback.format_exc())
        #     sys.exit(0)
        self.update_workers()

    # https://stackoverflow.com/questions/25382455/python-notimplementederror-pool-objects-cannot-be-passed-between-processes
    def __getstate__(self):
        self_dict = self.__dict__.copy()
        del self_dict['pool']
        return self_dict

    def __setstate__(self, state):
        self.__dict__.update(state)
