from enum import Enum


class TaskStatus(Enum):
    # 成功
    SUCCESS = 200
    # 服务连接超时
    SERVER_CONNECT_TIMEOUT = 504
    # 服务等待响应超时
    SERVER_READ_TIMEOUT = 505
    # 服务无法连接
    SERVER_NO_CONNECT = 502
    # 服务返回错误
    SERVER_FAIL = 503
    # worker 任务流验证失败
    WORKER_FLOW_VALID_FAIL = 601
    # worker 没有任务流
    WORKER_FLOW_NOT = 602
    # worker 执行失败
    WORKER_FAIL = 603

