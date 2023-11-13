from src.helper.logs import worker_async_logger


class WorkerError(Exception):
    def __init__(self, error_info="", record_stack=True):
        self.error_info = "客户端提交job失败：" + error_info
        if record_stack:
            worker_async_logger.exception(error_info)
        else:
            worker_async_logger.error(error_info)

    def __str__(self):
        return self.error_info


class WorkerStatusError(Exception):
    def __init__(self, status_code, message):
        self.message = message
        self.status_code = status_code
        worker_async_logger.exception(self)

    def __str__(self):
        return f"状态码{self.status_code}, 消息 {self.message}"


class WorkerSerializeError(WorkerError):
    def __init__(self):
        error_info = f"worker 数据序列化失败"
        super(WorkerSerializeError, self).__init__(error_info)


class WorkerNoFound(WorkerError):
    def __init__(self, worker=""):
        error_info = f"任务名称为 {worker} 的 worker 未找到"
        super(WorkerNoFound, self).__init__(error_info, False)


class WorkerTimeout(WorkerError):
    def __init__(self, worker="", timeout=0):
        error_info = f"任务名称为 {worker} 的 worker 执行超时, 超时时间 {timeout}"
        super(WorkerTimeout, self).__init__(error_info, False)


class NoResponseError(WorkerError):
    def __init__(self, worker=""):
        error_info = f"任务名称为 {worker} 的 worker 执行未获取到任何结果"
        super(NoResponseError, self).__init__(error_info, False)


class InvalidResponseError(WorkerError):
    def __init__(self, worker=""):
        error_info = f"任务名称为 {worker} 的 worker 返回的结果不合法"
        super(InvalidResponseError, self).__init__(error_info, False)
