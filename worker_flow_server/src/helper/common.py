import base64
import json
import pathlib
import re
import shutil
import socket
from datetime import datetime

import requests
import ulid
from fastapi import UploadFile

from src.config.base import DATA_PREFIX
from src.config.worker import UPLOAD_SERVER_URL


def str_to_list(value):
    """
    字符串转 string 数组
    :param value:
    :return:
    """
    data = re.split("[,，]", value)
    if "" in data:
        data.remove("")
    return data


def str_to_list_int(value):
    """
    字符串转 int 数组
    :param value:
    :return:
    """
    data = re.split("[,，]", value)
    if "" in data:
        data.remove("")
    data = [int(i) for i in data]
    return data


def get_local_ip():
    """
    获取 本地ip
    :return: ip
    """
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(('8.8.8.8', 80))
    ip = s.getsockname()[0]
    s.close()
    return ip


def gen_ulid():
    """
    随机生成ulid
    :return: ulid
    """
    return ulid.new().__str__()


def file_get_suffix(filename):
    """
    获取文件后缀
    :param filename: 文件名
    :return: 后缀
    """
    try:
        return filename.rsplit(".", 1)[1]
    except:
        return ""


def bytes_c_base64(b: bytes):
    return base64.b64encode(b).decode('utf-8')


def base64_c_bytes(bs64: str):
    return base64.b64decode(bs64)


def save_file(f: UploadFile):
    if not f:
        return None
    filename = "{}.{}".format(gen_ulid(), file_get_suffix(f.filename))

    today = datetime.today()
    relative_path = pathlib.Path("asset", today.strftime("%Y%m"), today.strftime("%d"))
    complete_path = pathlib.Path(DATA_PREFIX, relative_path)

    file_path = str(pathlib.Path(relative_path, filename)).replace("\\", "/")
    save_path = str(pathlib.Path(complete_path, filename)).replace("\\", "/")
    pathlib.Path(complete_path).mkdir(parents=True, exist_ok=True)
    with open(save_path, "wb") as destination:
        shutil.copyfileobj(f.file, destination)
    return file_path


def upload_file(file: bytes, suffix):
    """
    上传文件
    :param file: bytes
    :param suffix: 后缀
    :return:
    """
    result = {"success": False, "message": "", "data": ""}
    try:
        response = requests.post(UPLOAD_SERVER_URL, files={"file": (f"1.{suffix}", file)})
        if response.status_code != 200:
            result["message"] = "上传失败"
        else:
            result["data"] = json.loads(response.text)["data"]["file_path"]
            result["success"] = True
    except BaseException as e:
        result["message"] = str(e)
    return result
