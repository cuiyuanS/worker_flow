import json

from src.config.worker import ASYNC_JOB_ADDRESS
from src.worker.gearman_sync_help.client import JobsHandler
from src.node.execute import WorkerExecutor
from src.helper.logs import worker_async_logger
from src.worker.task_status import TaskStatus


class WorkerAsync:

    def __init__(self, gearman_worker, gearman_job):
        self.gearman_worker = gearman_worker
        self.gearman_job = gearman_job
        self.input_stream = gearman_job.data["data"]
        self.job_handler = JobsHandler(address=ASYNC_JOB_ADDRESS)
        self.res = {}

    def prepare(self):
        pass

    def run(self):
        chain_worker = WorkerExecutor(self.__class__.__name__)
        chain_worker.get_worker_flow_json()
        res = chain_worker.execute_flow()
        return res

    def finish(self):
        pass

    def finish_error(self):
        worker_async_logger.error(
            f"worker 任务处理失败 项目标记 {self.__class__.__name__} 错误消息 {json.dumps(self.res)}")

    def _run(self):
        try:
            self.prepare()
            # {'code': 200, 'message': '', 'data': {'ModelPath': 'http://10.25.10.132:8999/asset/202309/15/01HABPXETK14XZT9MZBKG1T59M.fbx'}}
            self.res = self.run()
            if self.res["code"] != 200:
                self.finish_error()
            else:
                self.finish()
        except Exception as e:
            message = f'任务处理失败 项目标记 {self.__class__.__name__} 异常消息 {str(e)}'
            worker_async_logger.exception(message)
            self.res["code"] = TaskStatus.WORKER_FAIL.value
            self.res["message"] = message
        finally:
            return self.res
