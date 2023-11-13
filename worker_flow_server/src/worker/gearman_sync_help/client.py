import traceback

from src.worker.gearman_help.util import GearmanJsonClient, GearmanPickleClient

from enum import Enum


class SerializeType(Enum):
    JSON = GearmanJsonClient
    PICKLE = GearmanPickleClient


# 封装 client 客户端调用程序
class SendJobs:

    def __init__(self, task_name, timeout=300, address=None, serialize_type=SerializeType.JSON):
        if address is None:
            address = ["127.0.0.1:4730"]
        self.task_name = task_name  # 功能函数
        self.timeout = timeout
        self.gm_client = serialize_type.value(address)  # 可用 ip 列表中 如果有无法连接的主机 会导致任务挂起 延时，知道连接重试结束
        self.jobs = []

    def add_job(self, param):
        self.jobs.append(dict(task=self.task_name, data=param))

    def wait_for_res(self):
        # 等待直到完成
        submitted_requests = self.gm_client.submit_multiple_jobs(self.jobs, background=False, wait_until_complete=False)
        # 超时时间
        if self.timeout:
            completed_requests = self.gm_client.wait_until_jobs_completed(submitted_requests,
                                                                          poll_timeout=self.timeout * len(self.jobs))
        else:
            completed_requests = self.gm_client.wait_until_jobs_completed(submitted_requests)
        return [job_request.result if job_request.result else None for job_request in completed_requests]

    def close(self):
        try:
            self.gm_client.shutdown()
        except:
            traceback.print_exc()


class JobsHandler:
    def __init__(self, address=["127.0.0.1:4730"]):
        self._global_data = {}  # 任务传递过程中需要使用的 全局数据 data 例如 u3d 可执行文件路径等等
        self.parent = []  # 责任链 历史请求
        self.job_address = address  # 可选的 gearman 地址

    @property
    def global_data(self):
        return self._global_data

    @global_data.setter
    def global_data(self, global_data):
        self._global_data = global_data

    def add_parent(self, obj):
        self.parent.append(obj)

    def dojob(self, task_name, data, timeout=0):
        """
        同步执行单任务
        :param task_name: 任务名称
        :param data:  数据
        :param timeout: 超时时间
        :return: 任务结果
        """
        jobs = SendJobs(task_name, timeout, self.job_address)
        # jobs.add_job(self.global_data, data)
        jobs.add_job(data)
        rs = jobs.wait_for_res()[0]
        jobs.close()
        return rs