import inspect
import os
import time

from src.helper.common import get_local_ip
from src.worker.worker_run_error import *


class Worker:
    """worker 功能函数 父类接口"""

    def __init__(self, gearman_worker, gearman_job, logger):
        self.gearman_worker = gearman_worker
        self.gearman_job = gearman_job
        self.data = gearman_job.data
        self.logger = logger
        self.this_server_ip = get_local_ip()

    @property
    def worker_id(self):
        return self.gearman_worker.worker_client_id

    def prepare(self):
        """
        run 前执行
        :return:
        """
        pass

    def run(self):
        raise NotImplementedError

    def finish(self):
        """
        成功
        :return:
        """
        pass

    def finish_error(self):
        """
        失败
        :return:
        """
        pass

    def _run(self):
        start = time.time()
        try:
            self.logger.info(f'开始任务 {self.__class__.__name__}')
            print(f'开始任务 {self.__class__.__name__}')
            # self.logger.info("data:" + json.dumps(data))
            self.prepare()
            rs = self.run()
            self.logger.info(f'完成任务 {self.__class__.__name__}')
            print(f'完成任务 {self.__class__.__name__}')
            end = time.time()
            self.logger.info("时间: %s" % (end - start))
            print("时间: %s" % (end - start))
            self.finish()
        except WorkerError as e:
            print(f'{str(e)}')
            self.finish_error()
            raise Exception(str(e)) from WorkerError
        except Exception as e:
            print(f'发生错误 {self.__class__.__name__} 消息：{str(e)}')
            self.finish_error()
            raise WorkerOtherError(self.__class__.__name__, str(e), self.logger) from e

        return rs

    @staticmethod
    def get_cur_info(depth=1):
        """获取执行堆栈信息"""
        try:
            current_frame = inspect.currentframe()
            for i in range(depth):
                current_frame = current_frame.f_back
            return os.path.basename(
                current_frame.f_code.co_filename), current_frame.f_lineno, current_frame.f_code.co_name
        except ValueError:
            return 'unknown', 0, 'unknown'
