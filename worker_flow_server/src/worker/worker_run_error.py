from src.worker.worker_sync_log import WorkerLogger


class BaseError(Exception):
    def __init__(self, base_error="", logger: WorkerLogger = None, p_stack=True):
        self.error_info = base_error
        self.logger = logger
        self.p_stack = p_stack
        self.send_logger()

    def send_logger(self):
        if self.logger:
            if self.p_stack:
                self.logger.exception(self.error_info)  # 错误堆栈
            else:
                self.logger.error(self.error_info)  # 只是错误消息

    def __str__(self):
        return self.error_info


class WorkerServerError(BaseError):
    def __init__(self, error_info="", logger: WorkerLogger = None, p_stack=True):
        message = f"worker server脚本错误: {error_info}"
        super(WorkerServerError, self).__init__(message, logger, p_stack)


class WorkerServerJobConnectError(WorkerServerError):
    def __init__(self, address_list=[], logger: WorkerLogger = None):
        info = f"gearman job连接失败 地址: {str(address_list)}"
        super(WorkerServerJobConnectError, self).__init__(error_info=info, logger=logger, p_stack=False)


class WorkerConfigRequestError(WorkerServerError):
    def __init__(self, error_info="", logger: WorkerLogger = None):
        info = f"请求 worker 配置信息失败 错误信息" + error_info
        super(WorkerConfigRequestError, self).__init__(error_info=info, logger=logger, p_stack=False)


class WorkerServerRequestConnectError(WorkerServerError):
    def __init__(self, url="", logger: WorkerLogger = None):
        info = f"网络连接错误, url: {url}"
        super(WorkerServerRequestConnectError, self).__init__(error_info=info, logger=logger, p_stack=False)


class WorkerServerRequestNoSuccessError(WorkerServerError):
    def __init__(self, status_code=500, url="", content="", logger: WorkerLogger = None):
        info = f"请求错误响应码 url: {url}, 状态码: {status_code}, 响应内容: {content}"
        super(WorkerServerRequestNoSuccessError, self).__init__(error_info=info, logger=logger, p_stack=False)


class WorkerServerErrorResponse(WorkerServerError):
    def __init__(self, url="", content="", logger: WorkerLogger = None):
        info = f"请求响应错误消息 url: {url}, 错误消息: {content}"
        super(WorkerServerErrorResponse, self).__init__(error_info=info, logger=logger, p_stack=False)


class WorkerRequestInvalidResponse(WorkerServerError):
    def __init__(self, url="", content="", logger: WorkerLogger = None):
        info = f"请求响应内容不合法 url: {url}, 响应内容: {content}"
        super(WorkerRequestInvalidResponse, self).__init__(error_info=info, logger=logger, p_stack=False)


class WorkerError(BaseError):
    def __init__(self, error_info="", logger: WorkerLogger = None):
        message = error_info
        super(WorkerError, self).__init__(message, logger)


class WorkerExecuteError(WorkerError):
    def __init__(self, worker="", error_info="", logger: WorkerLogger = None):
        message = f"worker {worker} 执行错误: " + error_info
        super(WorkerExecuteError, self).__init__(error_info=message, logger=logger)  # 初始化父类


class WorkerRedisError(WorkerError):
    def __init__(self, worker="", error_info="", logger: WorkerLogger = None):
        message = f"worker {worker} 记录redis错误: " + error_info
        super(WorkerRedisError, self).__init__(error_info=message, logger=logger)  # 初始化父类


class WorkerNotFound(WorkerExecuteError):
    def __init__(self, worker_name="", error_info="", logger: WorkerLogger = None):
        info = f"获取 {worker_name} 失败,错误: {error_info} "
        super(WorkerNotFound, self).__init__(error_info=info, logger=logger)


class LogGetError(WorkerExecuteError):
    def __init__(self, error_info="", logger: WorkerLogger = None):
        info = "获取日志文件失败 " + error_info
        super(LogGetError, self).__init__(error_info=info, logger=logger)


class NoInputError(WorkerExecuteError):
    def __init__(self, worker="", logger: WorkerLogger = None):
        info = "任务输入为空"
        super(NoInputError, self).__init__(worker=worker, error_info=info, logger=logger)


class NoOptionError(WorkerExecuteError):
    def __init__(self, worker="", error_info="", logger: WorkerLogger = None):
        info = "未找到的config.ini配置: " + error_info
        super(NoOptionError, self).__init__(worker=worker, error_info=info, logger=logger)


class InvalidInputError(WorkerExecuteError):
    def __init__(self, worker="", logger: WorkerLogger = None):
        info = "不合法的输入"
        super(InvalidInputError, self).__init__(worker=worker, error_info=info, logger=logger)


class ExecuteEmptyError(WorkerExecuteError):
    def __init__(self, worker="", logger: WorkerLogger = None):
        info = "执行未识别 可执行为空"
        super(ExecuteEmptyError, self).__init__(worker=worker, error_info=info, logger=logger)


class CommandExecuteError(WorkerExecuteError):
    def __init__(self, worker="", execute="", input_stream="", error_info="", logger: WorkerLogger = None):
        info = f"命令执行错误 可执行路径: {execute}, 输入: {str(input_stream)}, 错误消息: {error_info}"
        super(CommandExecuteError, self).__init__(worker=worker, error_info=info, logger=logger)


class FuncNotFoundError(WorkerExecuteError):
    def __init__(self, worker="", func="", logger: WorkerLogger = None):
        info = f"未找到可识别的Python任务函数 {func}"
        super(FuncNotFoundError, self).__init__(worker=worker, error_info=info, logger=logger)


class FuncExecuteError(WorkerExecuteError):
    def __init__(self, worker="", func="", input_stream="", error_info="", logger: WorkerLogger = None):
        info = f"Python任务函数执行错误, 函数: {func}, 输入, {input_stream}, 错误消息 {error_info}"
        super(FuncExecuteError, self).__init__(worker=worker, error_info=info, logger=logger)


class PythonCommandExecuteError(WorkerExecuteError):
    def __init__(self, worker="", execute="", input_stream="", error_info="", logger: WorkerLogger = None):
        info = f"Python命令执行错误, 路径: {execute}, 输入, {input_stream}, 错误消息 {error_info}"
        super(PythonCommandExecuteError, self).__init__(worker=worker, error_info=info, logger=logger)


class RequestConnectError(WorkerExecuteError):
    def __init__(self, worker="", url="", logger: WorkerLogger = None):
        info = f"网络连接失败, url: {url}"
        super(RequestConnectError, self).__init__(worker=worker, error_info=info, logger=logger)


class RequestNoSuccessError(WorkerExecuteError):
    def __init__(self, worker="", status_code=500, url="", input_stream="", content="", logger: WorkerLogger = None):
        info = f"网络请求错误响应 url: {url}, 输入: {input_stream}, 状态码: {status_code}, 响应内容: {content}"
        super(RequestNoSuccessError, self).__init__(worker=worker, error_info=info, logger=logger)


class RequestInvalidResponse(WorkerExecuteError):
    def __init__(self, worker="", url="", content="", logger: WorkerLogger = None):
        info = f"网络请求响应内容不合法 url: {url}, 响应内容: {content}"
        super(RequestInvalidResponse, self).__init__(worker=worker, error_info=info, logger=logger)


class WorkerOtherError(WorkerExecuteError):
    def __init__(self, worker="", error_info="", logger: WorkerLogger = None):
        info = f"消息: {error_info} "
        super(WorkerOtherError, self).__init__(worker=worker, error_info=info, logger=logger)


class WorkerResUploadError(WorkerExecuteError):
    def __init__(self, worker="", local_path="", logger: WorkerLogger = None):
        info = f"上传文件错误 本地路径: {local_path}"
        super(WorkerResUploadError, self).__init__(worker=worker, error_info=info, logger=logger)


class RedisRequestConnectError(WorkerRedisError):
    def __init__(self, url="", logger: WorkerLogger = None):
        info = f"网络连接失败, url: {url}"
        super(RedisRequestConnectError, self).__init__(error_info=info, logger=logger)


class RedisRequestNoSuccessError(WorkerRedisError):
    def __init__(self, status_code=500, url="", content="", logger: WorkerLogger = None):
        info = f"网络请求错误响应 url: {url}, 状态码: {status_code}, 响应内容: {content}"
        super(RedisRequestNoSuccessError, self).__init__(error_info=info, logger=logger)


class RedisErrorResponse(WorkerRedisError):
    def __init__(self, url="", content="", logger: WorkerLogger = None):
        info = f"网络请求响应错误消息 url: {url}, 响应内容: {content}"
        super(RedisErrorResponse, self).__init__(error_info=info, logger=logger)


class RedisRequestInvalidResponse(WorkerRedisError):
    def __init__(self, url="", content="", logger: WorkerLogger = None):
        info = f"网络请求响应内容不合法 url: {url}, 响应内容: {content}"
        super(RedisRequestInvalidResponse, self).__init__(error_info=info, logger=logger)
