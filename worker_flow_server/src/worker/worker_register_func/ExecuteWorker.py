import importlib

from src.worker.common import worker_url_request, worker_gearman_request
from src.worker.task_status import TaskStatus
from src.worker.worker_run_error import *
from src.worker.gearman_sync_help.worker import Worker


class ExecuteWorker(Worker):
    def run(self):
        config_data = self.data.get("config", {})
        timeout = self.data.get("timeout", 0)
        input = self.data.get("input", "")
        execute = config_data.get("execute", "")
        execute_kind = config_data.get("execute_kind", 0)

        if not execute:
            raise ExecuteEmptyError(self.__class__.__name__, self.logger)

        result = {"code": TaskStatus.WORKER_FAIL.value, "message": "", "data": None}

        if execute_kind == 1:
            from src.helper.service_process import subprocess_process
            command = execute
            for key, value in input.items():
                if type(value) == str:
                    command += " -{} '{}'".format(key, value)
                elif type(value) == int:
                    command += " -{} {}".format(key, value)
            try:
                suc, res = subprocess_process(command, timeout=timeout)
                if not suc:
                    result["message"] = res
                    result["code"] = TaskStatus.SERVER_FAIL.value
                    return result
            except Exception as e:
                raise CommandExecuteError(self.__class__.__name__, execute, {}, str(e), self.logger)
        elif execute_kind == 2:
            # python 函数
            importlib.invalidate_caches()
            try:
                _module = importlib.import_module("app.worker.worker_execute_func.%s" % execute)
                func = getattr(_module, "main")
            except:
                raise FuncNotFoundError(self.__class__.__name__, execute, self.logger)
            try:
                res = func(**input)
            except Exception as e:
                raise FuncExecuteError(self.__class__.__name__, execute, input, str(e), self.logger)
        elif execute_kind == 3:
            command = "python {}".format(execute)
            for key, value in input.items():
                command += " -{}={}".format(key, value)
            try:
                res = subprocess_process(command)
            except Exception as e:
                raise PythonCommandExecuteError(self.__class__.__name__, execute, input, str(e))
        elif execute_kind == 4:
            request_method = config_data.get("request_method", "post")
            body_method = config_data.get("body_method", "formData")
            response_method = config_data.get("response_method", "json")
            # from src.helper.common import base64_c_bytes
            # response = {"success": True, "data": {"content": base64_c_bytes(input["fileb"])}}
            response = worker_url_request(url=execute, data=input, timeout=(2, timeout), request_method=request_method,
                                          body_method=body_method, response_method=response_method)
            if not response["success"]:
                result["code"] = response["code"]
                result["message"] = f'api 请求失败 {response["message"]}'
                return result
            res = response["data"]
        elif execute_kind == 5:
            # gearman 请求
            task = config_data.get("task", "")
            response = worker_gearman_request(job_address=execute, task=task, data=input, timeout=timeout)
            if not response["success"]:
                result["code"] = response["code"]
                result["message"] = f'api 请求失败 {response["message"]}'
                return result
            res = response["data"]
        else:
            self.logger.error("执行类型未识别")
            return
        result["data"] = res
        result["code"] = TaskStatus.SUCCESS.value
        return result
