import logging
import os
import pathlib


from src.config.base import *
from src.helper.common import get_local_ip
from src.middleware.global_ctx import g

_srcfile = os.path.normcase(logging.addLevelName.__code__.co_filename)


class CustomLogger(logging.Logger):
    # 自定义 logger 填充额外信息
    def __init__(self, name, level=logging.NOTSET):
        super().__init__(name, level)
        self.extra = {'host_ip': get_local_ip(), "address": g.client_ip}

    def _log(self, level, msg, args, exc_info=None, extra=None, stack_info=False,
             stacklevel=1):
        if extra is None:
            extra = self.extra
        else:
            extra.update(self.extra)
        super(CustomLogger, self)._log(level, msg, args, exc_info, extra, stack_info, stacklevel)


# python默认的输出会将消息原样输出，如果有异常的话，会将异常堆栈多行形式返回。不方便进行日志的收集分析。所以需要将其输出为一行。
class WebServerLogFormatter(logging.Formatter):
    '''将换行转义'''

    def __init__(self, fmt=None, datefmt=None, style='%', validate=True):
        super(WebServerLogFormatter, self).__init__(fmt, datefmt, style, validate)

    def format(self, record):
        msg: str = super().format(record)
        if record.levelno == logging.ERROR:
            pass
            # send_web_server_message(msg)
        if ENVIRONMENT in ["dev"]:
            return msg
        else:
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


def get_web_server_logger():
    fmt = WebServerLogFormatter(fmt="%(asctime)s # "
                                    "client ip %(address)s # "
                                    "host ip %(host_ip)s # "
                                    "%(levelname)s # "
                                    "%(name)s # "
                                    "%(filename)s # "
                                    "%(funcName)s # "
                                    "Line=%(lineno)s # "
                                    "Msg=%(message)s", datefmt="%Y-%m-%d %H:%M:%S")

    log_dir = pathlib.Path(LOG_DIR, PROJECT_NAME)
    if not log_dir.exists():
        log_dir.mkdir(parents=True, exist_ok=True)
    if ENVIRONMENT in ["dev"]:
        error_handler = logging.StreamHandler()
    else:
        error_handler = logging.FileHandler(pathlib.Path(log_dir, 'error.log'), mode="a", encoding='utf-8')
    error_handler.setFormatter(fmt)
    error_handler.addFilter(LevelFilter(logging.ERROR))

    if ENVIRONMENT in ["dev"]:
        info_handler = logging.StreamHandler()
    else:
        info_handler = logging.FileHandler(pathlib.Path(log_dir, 'info.log'), mode="a", encoding='utf-8')
    info_handler.setFormatter(fmt)
    info_handler.addFilter(LevelFilter(logging.INFO))

    logger = CustomLogger("web_server")
    logger.addHandler(error_handler)
    logger.addHandler(info_handler)
    logger.setLevel(logging.INFO)
    return logger

def get_worker_async_logger():
    fmt = WebServerLogFormatter(fmt="%(asctime)s # "
                                    "host ip %(host_ip)s # "
                                    "%(levelname)s # "
                                    "%(name)s # "
                                    "%(filename)s # "
                                    "%(funcName)s # "
                                    "Line=%(lineno)s # "
                                    "Msg=%(message)s", datefmt="%Y-%m-%d %H:%M:%S")

    log_dir = pathlib.Path(LOG_DIR, PROJECT_NAME + "_worker_async")
    if not log_dir.exists():
        log_dir.mkdir(parents=True, exist_ok=True)
    if ENVIRONMENT in ["dev"]:
        error_handler = logging.StreamHandler()
    else:
        error_handler = logging.FileHandler(pathlib.Path(log_dir, 'error.log'), mode="a", encoding='utf-8')
    error_handler.setFormatter(fmt)
    error_handler.addFilter(LevelFilter(logging.ERROR))

    if ENVIRONMENT in ["dev"]:
        info_handler = logging.StreamHandler()
    else:
        info_handler = logging.FileHandler(pathlib.Path(log_dir, 'info.log'), mode="a", encoding='utf-8')
    info_handler.setFormatter(fmt)
    info_handler.addFilter(LevelFilter(logging.INFO))

    logger = CustomLogger("worker_async")
    logger.addHandler(error_handler)
    logger.addHandler(info_handler)
    logger.setLevel(logging.INFO)
    return logger



web_logger = get_web_server_logger()
worker_async_logger = get_worker_async_logger()
