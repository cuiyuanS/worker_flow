import time

from requests import ConnectTimeout, ReadTimeout, ConnectionError
import requests

from src.worker.gearman_help.admin_client import AdminClient
from src.worker.gearman_help.util import GearmanJsonClient
from src.worker.task_status import TaskStatus


def worker_url_request(url, data, timeout=None, request_method="post", body_method="formData", response_method="json"):
    """
    worker url请求
    :param url:
    :param data:
    :return:
    """
    result = {"success": False, "message": "", "data": {}, "code": TaskStatus.SUCCESS.value}
    try:
        if request_method == "post":
            if body_method == "formData":
                response = requests.post(url, data=data, timeout=timeout)
            else:
                response = requests.post(url, json=data, timeout=timeout)
        else:
            response = requests.get(url, params=data, timeout=timeout)
    except ConnectTimeout as e:
        result["code"] = TaskStatus.SERVER_CONNECT_TIMEOUT.value
        result["message"] = f"网络连接超时 地址：{url}"
        return result
    except ReadTimeout as e:
        result["code"] = TaskStatus.SERVER_READ_TIMEOUT.value
        result["message"] = f"等待响应超时 地址：{url}"
        return result
    except ConnectionError as e:
        result["code"] = TaskStatus.SERVER_NO_CONNECT.value
        result["message"] = f"网络连接异常 地址：{url}"
        return result
    try:
        if response.status_code != 200:
            result["code"] = TaskStatus.SERVER_FAIL.value
            result["message"] = f"服务异常状态码 地址：{url} 响应码 {response.status_code}"
        else:
            result["message"] = ''
            if response_method == "json":
                try:
                    res = response.json()
                    result["success"] = True
                    result["data"] = res
                except:
                    result["code"] = TaskStatus.SERVER_FAIL.value
                    result["message"] = f"服务响应非法json 地址：{url}"
            else:
                result["success"] = True
                result["data"] = {
                    "content": response.content
                }

    except BaseException as e:
        result["code"] = TaskStatus.SERVER_FAIL.value
        result["message"] = f"服务异常 {str(e)}"
    return result


def worker_gearman_request(job_address, task, data, timeout=None):
    """
    worker gearman请求
    :param job_address:
    :param task:
    :param data:
    :param timeout:
    :return:
    """
    result = {"success": False, "message": "", "data": {}, "code": TaskStatus.SUCCESS.value}
    gearman_admin = AdminClient(address=[job_address])
    connect_suc = gearman_admin.try_connect()
    if not connect_suc:
        result["code"] = TaskStatus.SERVER_NO_CONNECT.value
        result["message"] = f"外部 gearman job 地址 {job_address} 无法连接"
        return result
    status = gearman_admin.get_workers_status()
    for i in status:
        if i["task"] == task and i["workers"] != 0:
            exist = True
            break
    else:
        exist = False
    if not exist:
        result["code"] = TaskStatus.SERVER_NO_CONNECT.value
        result["message"] = f"外部 worker {task} 未找到, gearman job 地址为 {job_address}"
        return result

    client = GearmanJsonClient([job_address])
    start = time.time()
    response = client.submit_job(task, data, background=False, poll_timeout=timeout)
    end = time.time()
    total_time = end - start

    if not response.result:
        if timeout and total_time > timeout:
            result[
                "message"] = f"外部 worker {task} 执行超时 超时时间 {timeout}, gearman job 地址为 {job_address}"
            result["code"] = TaskStatus.SERVER_READ_TIMEOUT.value
        else:
            result["message"] = f"外部 worker {task} 未返回结果, gearman job 地址为 {job_address}"
            result["code"] = TaskStatus.SERVER_FAIL.value
        return result
    result["data"] = response.result
    return result


def post_json(url, json):
    """
    异步回调通知
    :param url:
    :param json:
    :return:
    """
    result = {"success": False, "message": "", "data": {}}
    try:
        response = requests.post(url, json=json)
    except:
        result["message"] = f"网络连接异常 无法连接 地址：{url}"
        return result
    try:
        if response.status_code != 200:
            result["message"] = f"异常状态码 地址：{url} 响应码 {response.status_code}"
        else:
            result["message"] = ''
            result["success"] = True
    except BaseException as e:
        result["message"] = str(e)
    return result
