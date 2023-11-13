import json
import multiprocessing
import os
import signal
import socket
import sys
import threading
import time
from copy import copy

from src.config.worker import SYNC_JOB_ADDRESS
from src.worker.gearman_help.util import GearmanJsonWorker
from src.worker.gearman_sync_help.gearman_lib import TaskObj
from src.lib.gearman.errors import ServerUnavailable
from src.worker.worker_run_error import *

from src.helper.common import get_local_ip
from src.worker.worker_sync_log import get_worker_server_handler

stop_thread = False


def init_pool_processes(the_lock):
    '''Initialize each process with a global variable lock.
    '''
    signal.signal(signal.SIGINT, signal.SIG_IGN)
    global lock
    lock = the_lock


class WorkerServer:
    """
    根据配置 注册并管理 多线程 worker
    """

    def __init__(self):
        self.workers = manager.dict()
        self.this_server_host = socket.gethostname()
        self.logger = get_worker_server_handler()
        self.this_server_ip = get_local_ip()
        self.worker_config = {}
        self.threads_id = 0
        self.pools = []

    def get_worker_config(self):
        """获取worker config 配置"""
        # url = self.server_url + "/api/worker/config_info"
        # while True:
        #     try:
        #         response = requests.get(self.server_url + "/api/worker/config_info")
        #     except:
        #         WorkerServerRequestConnectError(url, self.logger)
        #         self.logger.info("获取 worker 信息失败 重试中")
        #         time.sleep(2)
        #         continue
        #
        #     if response.status_code != 200:
        #         WorkerServerRequestNoSuccessError(response.status_code, url, response.content, self.logger)
        #         self.logger.info("获取 worker 信息失败 重试中")
        #         time.sleep(2)
        #         continue
        #     else:
        #         try:
        #             data = json.loads(response.content)
        #             err = data["err"]
        #         except:
        #             WorkerRequestInvalidResponse(url, response.content.decode("utf-8"), self.logger)
        #             self.logger.info("获取 worker 信息失败 重试中")
        #             time.sleep(2)
        #             continue
        #         if err:
        #             WorkerServerErrorResponse(url, err)
        #             self.logger.info("获取 worker 信息失败 重试中")
        #             time.sleep(2)
        #             continue
        #     break

        with open("src/config/worker_distribution.json", "r") as f:
            data = json.load(f)
        t = {}
        for info in data:
            job_address = info.pop("job_address", [])
            if not self.re_this_server(job_address):
                continue
            t[info["cla_name"]] = info
        return t

    def get_threads_id(self):
        self.threads_id += 1
        return self.threads_id

    def update_worker_config(self):
        """
        更新 worker 配置 文件 以及 要连接 的 job ip
        :return:
        """
        data = self.get_worker_config()
        return data

    def register_task(self, task_name, func, job_address_list):
        """
        注册任务
        :param job_address_list: job ip 地址
        :param task_name: 任务名
        :param func: 函数名
        :return:
        """
        def stop(signum, frame):
            gm_worker.shutdown()
            sys.exit(0)
        signal.signal(signal.SIGTERM, stop)
        if not job_address_list:
            self.logger.error("job ip not found")
            return
        # worker 注册 task 一个 task  多个 worker
        gm_worker = GearmanJsonWorker(job_address_list)
        try:
            client_id = "worker_" + self.this_server_ip + "_" + task_name + "_" + str(self.get_threads_id())
            gm_worker.set_client_id(client_id)
            gm_worker.register_task(task_name.encode("utf-8"), func)
            lock.acquire()
            self.workers[task_name].append(multiprocessing.current_process().pid)
            lock.release()
            try:
                self.logger.info(f"registered {task_name} client_id {client_id}")
                gm_worker.work()
            except ServerUnavailable:
                raise WorkerServerJobConnectError(job_address_list, self.logger)
        except WorkerServerJobConnectError as e:
            self.logger.error("job断开5s后重试")
            time.sleep(5)
            self.register_task(task_name, func, job_address_list)
        finally:
            gm_worker.unregister_task(task_name)
            self.logger.info("unregister_task " + task_name)

    def re_this_server(self, host_server):
        # # 判断ip 是否是 本机ip
        for ip in host_server:
            if self.this_server_ip in ip:
                return True
            elif self.this_server_ip == ip:
                return True

        return False

    def shutdown_all_task_by_task_name(self, task_name):
        # 关闭所有注册这个 task_name 的worker
        gearman_workers = self.workers[task_name]
        for i in gearman_workers:
            os.kill(i, signal.SIGTERM)
        self.logger.info('shutdown worker :' + task_name, extra={"address": self.this_server_ip})
        time.sleep(0.5)
        del (self.workers[task_name])

    def update_workers(self, new_config, is_thread=False):
        server_info = {
            "host": self.this_server_host,
        }
        if new_config != self.worker_config:
            # global pool
            worker_num = 0
            self.worker_config = new_config
            if not self.worker_config:
                return
            self.logger.info("worker 配置更新")
            for task_name, info in new_config.items():
                if task_name in self.workers and len(self.workers[task_name]) != info["t_nun"]:
                    self.shutdown_all_task_by_task_name(task_name)
            difference = [x for x in self.workers.keys() if x not in new_config.keys()]
            for task_name in difference:
                self.shutdown_all_task_by_task_name(task_name)

            for task_name, info in self.worker_config.items():
                server_info["cla_name"] = info["cla_name"]
                if task_name in self.workers:
                    continue
                worker_num += info["t_nun"]
            if not worker_num:
                return
            pool = multiprocessing.Pool(initializer=init_pool_processes, initargs=(lock,), processes=worker_num)
            # pool = multiprocessing.Pool(processes=worker_num)
            self.pools.append(pool)
            for task_name, info in self.worker_config.items():
                server_info["cla_name"] = info["cla_name"]
                if task_name in self.workers:
                    continue
                self.workers[task_name] = manager.list()
                for n in range(info["t_nun"]):
                    args = (task_name, TaskObj(self, copy(server_info)).task_func, SYNC_JOB_ADDRESS)
                    pool.apply_async(func=self.register_task, args=args, error_callback=self.pool_exception)
            # if is_thread:
            #     global stop_thread
            #     stop_thread = True
            #     time.sleep(0.1)
            #     stop_thread = False
            #     t = threading.Thread(target=self.keep_update_config)
            #     t.daemon = True
            #     t.start()
            try:
                pool.close()
                pool.join()
            except KeyboardInterrupt:
                return

    def pool_exception(self, exception):
        print(exception)

    def stop(self):
        # 停止所有worker
        # if pool:
        for pool in self.pools:
            pool.terminate()
            pool.join()
        # if hasattr(self, "workers") and self.workers:
        self.logger.info('worker server shutdown')
        sys.exit(0)  # 正常退出

    def start(self):
        # try:
        #     signal.signal(signal.SIGTERM, self.stop)
        # except Exception as e:
        #     self.logger.error(traceback.format_exc())
        #     sys.exit(0)
        self.logger.info('worker server started')
        # t = threading.Thread(target=self.keep_update_config)
        # 当设置一个线程为守护线程时，此线程所属进程不会等待此线程运行结束，进程将立即结束
        # t.daemon = True
        # t.start()
        worker_config = self.update_worker_config()
        try:
            self.update_workers(worker_config)
        except Exception as e:
            raise WorkerServerError(f"启动 worker server 失败: {str(e)}", self.logger)

    def keep_update_config(self):
        global stop_thread
        while not stop_thread:
            while True:
                time.sleep(5)
                new_config = self.get_worker_config()
                time.sleep(1)
                self.update_workers(new_config, is_thread=True)

    # https://stackoverflow.com/questions/25382455/python-notimplementederror-pool-objects-cannot-be-passed-between-processes
    def __getstate__(self):
        self_dict = self.__dict__.copy()
        if "pools" in self_dict:
            del self_dict['pools']
        return self_dict

    def __setstate__(self, state):
        self.__dict__.update(state)


manager = multiprocessing.Manager()
lock = multiprocessing.Lock()
