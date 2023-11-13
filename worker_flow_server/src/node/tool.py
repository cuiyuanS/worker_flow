import requests

from src.helper.common import bytes_c_base64, upload_file, base64_c_bytes
from src.node.constant import DataType


class UploadLocal:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required":
                {
                    "local_path": (DataType.LOCAL_PATH.name,)
                }
        }

    RETURN_TYPES = (DataType.CDN_PATH.name,)

    CATEGORY = "tool"

    def execute(self, local_path):
        return local_path.replace("/data/worker_flow/example/", "http://10.25.20.15:8001/"),


class Bs64ConvertBytes:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required":
                {
                    "bs64": (DataType.BS64.name,)
                }
        }

    RETURN_TYPES = (DataType.BYTES.name,)

    CATEGORY = "tool"

    def execute(self, bs64):
        return base64_c_bytes(bs64),


class BytesConvertBs64:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required":
                {
                    "bytes": (DataType.BYTES.name,)
                }
        }

    RETURN_TYPES = (DataType.BS64.name,)

    CATEGORY = "tool"

    def execute(self, bytes):
        return bytes_c_base64(bytes),


class UploadBytes:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required":
                {
                    "suffix": (DataType.STRING.name, {"default": "mp4"}),
                    "bytes_data": (DataType.BYTES.name,)
                }
        }

    RETURN_TYPES = (DataType.CDN_PATH.name,)

    CATEGORY = "tool"

    def execute(self, suffix, bytes_data):
        result = upload_file(bytes_data, suffix)
        if not result["success"]:
            raise Exception(result["message"])
        return result["data"],


class CdnConvertBytes:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required":
                {
                    "cdn_path": (DataType.CDN_PATH.name, )
                }
        }

    RETURN_TYPES = (DataType.BYTES.name,)

    CATEGORY = "tool"

    def execute(self, cdn_path):
        response = requests.get(cdn_path)
        return response.content,


class HttpRequestPost:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required":
                {
                    "url": (DataType.LOCAL_PATH.name,),
                    "data": (DataType.JSON.name,),
                    "type": (DataType.INT.name,)
                }
        }

    RETURN_TYPES = (DataType.LOCAL_PATH.name,)

    CATEGORY = "tool"

    def execute(self, url, data, type):
        """

        :param url: 请求地址
        :param data: 请求体
        :param type: 请求类型 1:json 2:form
        :return:
        """
        pass


class HttpRequestGet:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required":
                {
                    "url": (DataType.LOCAL_PATH.name,),
                    "data": (DataType.JSON.name,),
                    "type": (DataType.INT.name,)
                }
        }

    RETURN_TYPES = (DataType.LOCAL_PATH.name,)

    CATEGORY = "tool"

    def execute(self, url, data, type):
        """

        :param url: 请求地址
        :param data: 请求体
        :param type: 请求类型 1:json 2:form
        :return:
        """
        pass
