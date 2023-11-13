import logging
import os
import sys

import pathlib

from src.config.base import LOG_DIR, PROJECT_NAME
from src.helper.common import get_local_ip

_srcfile = os.path.normcase(logging.addLevelName.__code__.co_filename)

this_server_ip = get_local_ip()


class WorkerLogger(logging.Logger):
    """
    重写 logger 添加自定义 finename funcName lineno 添加 地址
    """

    def _log(self, level, msg, args, finename="", funcName="", lineno=0, exc_info=None, extra=None, stack_info=False,
             stacklevel=1):
        if not extra:
            extra = {"address": this_server_ip}
        sinfo = None
        if all([finename, lineno, funcName]):
            fn, lno, func = finename, lineno, funcName
        else:

            if _srcfile:
                # IronPython doesn't track Python frames, so findCaller raises an
                # exception on some versions of IronPython. We trap it here so that
                # IronPython can use logging.
                try:
                    fn, lno, func, sinfo = self.findCaller(stack_info, stacklevel)
                except ValueError:  # pragma: no cover
                    fn, lno, func = "(unknown file)", 0, "(unknown function)"
            else:  # pragma: no cover
                fn, lno, func = "(unknown file)", 0, "(unknown function)"
            if exc_info:
                not_exception = True
                if isinstance(exc_info, BaseException):
                    exc_info = (type(exc_info), exc_info, exc_info.__traceback__)
                elif not isinstance(exc_info, tuple):
                    exc_info = sys.exc_info()
                    for i in exc_info:
                        if i:
                            not_exception = False
                            break
                if not_exception:
                    exc_info = None

        record = self.makeRecord(self.name, level, fn, lno, msg, args,
                                 exc_info, func, extra, sinfo)
        self.handle(record)


class WorkerFormatter(logging.Formatter):
    """
    python默认的输出会将消息原样输出，如果有异常的话，会将异常堆栈多行形式返回。不方便进行日志的收集分析。所以需要将其输出为一行。
    """
    def __init__(self, name="", fmt=None, datefmt=None, style='%', validate=True):
        super(WorkerFormatter, self).__init__(fmt, datefmt, style, validate)
        self.name = name

    def format(self, record):
        msg: str = super().format(record)
        if record.levelno == logging.ERROR:
            # 转换前 记录原样日志到飞书
            pass
        return msg.replace('\r\n', '\n').replace('\r', '\n').replace('\n', '\\n')


class LevelFilter(logging.Filter):
    """
    ERROR = 40
    WARNING = 30
    WARN = WARNING
    INFO = 20
    DEBUG = 10
    """

    def __init__(self, level, *args, **kwargs):
        logging.Filter.__init__(self, *args, **kwargs)
        self.level = level

    def filter(self, record):
        if record.levelno == self.level:
            return True
        return False


def get_worker_client_handler(worker_client_id):
    """实例化 worker 日志 logger"""
    fmt = WorkerFormatter(name=worker_client_id, fmt="%(asctime)s # "
                                                     "%(address)s # "
                                                     "%(levelname)s # "
                                                     "%(name)s # "
                                                     "%(filename)s # "
                                                     "%(funcName)s # "
                                                     "Line=%(lineno)s # "
                                                     "Msg=%(message)s", datefmt="%Y-%m-%d %H:%M:%S")

    log_dir = pathlib.Path(LOG_DIR, PROJECT_NAME + "_worker_sync/run")
    if not log_dir.exists():
        log_dir.mkdir(parents=True, exist_ok=True)

    error_handler = logging.FileHandler(pathlib.Path(log_dir, worker_client_id + '-error.log'), mode="a",
                                        encoding='utf-8')
    error_handler.setFormatter(fmt)
    # error_handler.setLevel(logging.ERROR)
    error_handler.addFilter(LevelFilter(logging.ERROR))

    info_handler = logging.FileHandler(pathlib.Path(log_dir, worker_client_id + '-info.log'), mode="a",
                                       encoding='utf-8')
    info_handler.setFormatter(fmt)
    # info_handler.setLevel(logging.INFO)
    info_handler.addFilter(LevelFilter(logging.INFO))

    logging.setLoggerClass(WorkerLogger)

    logger = logging.getLogger(worker_client_id)
    logger.addHandler(error_handler)
    logger.addHandler(info_handler)
    logger.setLevel(logging.INFO)

    return logger


def remove_logger_handler(logger):
    logger.handlers = []


def get_worker_server_handler():
    """实例化 worker_server 日志 logger"""
    fmt = WorkerFormatter(name="worker_server", fmt="%(asctime)s # "
                                                    "%(address)s # "
                                                    "%(levelname)s # "
                                                    "%(name)s # "
                                                    "%(filename)s # "
                                                    "%(funcName)s # "
                                                    "Line=%(lineno)s # "
                                                    "Msg=%(message)s", datefmt="%Y-%m-%d %H:%M:%S")

    log_dir = pathlib.Path(LOG_DIR, PROJECT_NAME + "_worker_sync/service")
    if not log_dir.exists():
        log_dir.mkdir(parents=True, exist_ok=True)

    error_handler = logging.FileHandler(pathlib.Path(log_dir, "error.log"), mode="a", encoding='utf-8')
    error_handler.setFormatter(fmt)
    # error_handler.setLevel(logging.ERROR)
    error_handler.addFilter(LevelFilter(logging.ERROR))

    info_handler = logging.FileHandler(pathlib.Path(log_dir, "info.log"), mode="a", encoding='utf-8')
    info_handler.setFormatter(fmt)
    # info_handler.setLevel(logging.INFO)
    info_handler.addFilter(LevelFilter(logging.INFO))

    logging.setLoggerClass(WorkerLogger)

    logger = logging.getLogger("worker_server")
    logger.addHandler(error_handler)
    logger.addHandler(info_handler)

    logger.setLevel(logging.INFO)
    return logger
