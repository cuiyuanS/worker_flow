import traceback

from src.lib.gearman.constants import *
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

    # params package
    def _default_job_param(self, data, callback_url="", userdata=None, tag="", timeout=0):
        return {
            "tag": tag,
            "data": data,
            "task_name": self.task_name,
            "callback_url": callback_url,
            "userdata": userdata,
            "timeout": timeout,
        }

    def add_job_async(self, param_json, callback_url, userdata, tag, timeout=0, priority=PRIORITY_LOW):
        rs = self.gm_client.submit_job(self.task_name,
                                       self._default_job_param(param_json, callback_url=callback_url, userdata=userdata,
                                                               tag=tag, timeout=timeout),
                                       background=True, priority=priority)
        return rs

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

    #
    def _dojobs_async_call_priority(self, task_name, data, callback_url="", userdata=None, tag="", timout=0,
                                    priority=PRIORITY_LOW, serialize_type=SerializeType.JSON):
        jobs = SendJobs(task_name, address=self.job_address, serialize_type=serialize_type)
        try:
            rs = jobs.add_job_async(data, callback_url, userdata, tag, timout, priority)
            jobs.close()
        except:
            return -1
        return rs.job.unique

    def dojob_async_call(self, task_name, data, callback_url="", userdata=None, tag="", timout=0, priority=PRIORITY_LOW,
                         serialize_type=SerializeType.JSON):
        """
        异步执行单任务
        :param timout: 链式任务超时事件
        :param task_name: 任务名称
        :param data: 数据
        :param callback_url: 回调地址
        :param userdata: 回调参数
        :param tag: 标签
        :param priority: 优先级
        :return:
        """
        return self._dojobs_async_call_priority(task_name, data, callback_url, userdata, tag, timout, priority,
                                                serialize_type)

    def dojobs_async_call(self, task_name, data, callback_url="", userdata=None, tag="", priority=PRIORITY_LOW,
                          serialize_type=SerializeType.JSON):
        """
        异步执行多任务
        :param task_name: 任务名称
        :param data: list data
        :param callback_url: 回调地址
        :param userdata: 回调参数
        :param tag: 标签
        :param priority: 优先级
        :return:
        """
        return [self._dojobs_async_call_priority(task_name, i, callback_url, userdata, tag, timout, priority,
                                                 serialize_type)
                for i in data]
