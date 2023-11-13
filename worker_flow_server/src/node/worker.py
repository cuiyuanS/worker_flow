import inspect
import time

from src.config.worker import SYNC_JOB_ADDRESS
from src.node.constant import DataType, AIGenModel_Sex
from src.worker.gearman_help.admin_client import AdminClient
from src.worker.gearman_sync_help.client import JobsHandler
from src.worker.task_status import TaskStatus
from src.worker.worker_error import *


def execute_extract_data(request_json, return_names):
    data = []
    for i in return_names:
        try:
            data.append(request_json[i])
        except:
            data.append(None)
    return tuple(data)


class WorkerNode:
    worker_cls: str = ""
    input_stream: dict = {}
    gearman_timeout: int = None
    request_timeout: int = None
    config = {}

    def execute(self, *args, **kwargs):
        self.input_stream["config"] = self.config
        self.input_stream["timeout"] = self.request_timeout
        self.input_stream["input"] = {}

        params = inspect.signature(self.execute).parameters
        # 遍历参数并打印参数名
        for i, param_name in enumerate(list(params)):
            self.input_stream["input"][param_name] = args[i]
        job_handler = JobsHandler(address=SYNC_JOB_ADDRESS)
        gearman_admin = AdminClient(address=job_handler.job_address)
        status = gearman_admin.get_workers_status()
        for i in status:
            if i["task"] == self.worker_cls and i["workers"] != 0:
                exist = True
                break
        else:
            exist = False
        if not exist:
            raise WorkerNoFound(self.worker_cls)

        start = time.time()
        response = job_handler.dojob(self.worker_cls, self.input_stream, timeout=self.gearman_timeout)

        end = time.time()
        total_time = end - start

        result = None

        if not response:
            if total_time > self.gearman_timeout:
                error = WorkerTimeout(self.worker_cls, self.gearman_timeout)
                result = {"code": TaskStatus.SERVER_READ_TIMEOUT, "message": error.error_info}
            else:
                error = NoResponseError(self.worker_cls)
                result = {"code": TaskStatus.WORKER_FAIL, "message": error.error_info}
        if not result: result = response

        if result["code"] != TaskStatus.SUCCESS.value:
            raise WorkerStatusError(status_code=result["code"], message=result["message"])

        data = result["data"]

        return data


class AIGenModelFFHQFlame(WorkerNode):
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required":
                {
                    "image_data": (DataType.BS64.name,),
                    "sex": (AIGenModel_Sex,),
                }
        }

    RETURN_TYPES = (
        DataType.LOCAL_PATH.name, DataType.LOCAL_PATH.name, DataType.LOCAL_PATH.name, DataType.LOCAL_PATH.name,
        DataType.LOCAL_PATH.name
    )
    RETURN_NAMES = ("texture_path", "left_eye_path", "right_eye_path", "obj_file_path", "obj_data_file_path")

    CATEGORY = "worker"

    worker_cls = "AIGenModelFFHQFlame"
    config = {
        "execute": "http://127.0.0.1:8990/demo",
        "execute_kind": 4,
    }
    gearman_timeout: int = 60
    request_timeout: int = 50

    def execute(self, image_data, sex):
        request_json = {
            "texture_path": "/data/worker_flow/example/AI3D/output/20231008065924/stage3_uv.png",
            "left_eye_path": "/data/worker_flow/example/AI3D/output/20231008065924/eyeball_l.txt",
            "right_eye_path": "/data/worker_flow/example/AI3D/output/20231008065924/eyeball_r.txt",
            "obj_file_path": "/data/worker_flow/example/AI3D/output/20231008065924/20231008065924.obj",
            "obj_data_file_path": "/data/worker_flow/example/AI3D/output/20231008065924/20231008065924_verts.txt"
        }
        # request_json = super(AIGenModelFFHQFlame, self).execute(image_data, sex)
        return execute_extract_data(request_json, self.RETURN_NAMES)


class MixEye(WorkerNode):
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required":
                {
                    "texture_path": (DataType.BYTES.name,),
                }
        }

    RETURN_TYPES = (DataType.BYTES.name,)

    RETURN_NAMES = ("texture_path",)

    CATEGORY = "worker"

    worker_cls = "MixEye"
    config = {
        "execute": "http://10.25.20.15:6000/worker_server_api/head_model_eyes_map",
        "execute_kind": 4,
        "response_method": "content"
    }
    gearman_timeout: int = None
    request_timeout: int = None

    def execute(self, texture_path):
        request_json = super(MixEye, self).execute(texture_path)
        return execute_extract_data(request_json, self.RETURN_NAMES)


class U3DFlameFFHQ:

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required":
                {
                    "ObjData": (DataType.CDN_PATH.name,),
                    "LeftEyeDataPath": (DataType.CDN_PATH.name,),
                    "RightEyeDataPath": (DataType.CDN_PATH.name,),
                    "TexturePath": (DataType.CDN_PATH.name,),
                }
        }

    RETURN_TYPES = (DataType.LOCAL_PATH.name,)

    RETURN_NAMES = ("ModelPath",)

    CATEGORY = "worker"

    worker_cls = "U3DFlameFFHQ"
    config = {
        "execute": "http://10.25.10.10:9001/u3d/flameFFHQ",
        "execute_kind": 4,
        "request_method": "get"
    }
    gearman_timeout: int = 60
    request_timeout: int = 50

    def execute(self, ObjData, LeftEyeDataPath, RightEyeDataPath, TexturePath):
        request_json = {
            "ModelPath": "/data/worker_flow/example/U3D/output/1696748464/859aa844-94ba-48d9-994f-64ba7ade40dbmodel.fbx",
        }
        # request_json = super(U3DFlameFFHQ, self).execute(ObjData, LeftEyeDataPath, RightEyeDataPath, TexturePath)
        return execute_extract_data(request_json, self.RETURN_NAMES)


class VideoStylization(WorkerNode):
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required":
                {
                    "bs64": (DataType.BS64.name,),
                    "style": (DataType.INT.name, {"default": 0, "min": 0, "max": 0xffffffffffffffff}),
                }
        }

    RETURN_TYPES = (DataType.BS64.name, DataType.BS64.name)

    RETURN_NAMES = ("data", "first_image")

    CATEGORY = "worker"

    worker_cls = "VideoStylization"
    config = {
        "execute": "10.25.20.15:4730",
        "execute_kind": 5,
        "task": "mov2mov"
    }
    gearman_timeout: int = None
    request_timeout: int = None

    def execute(self, bs64, style):
        request_json = super(VideoStylization, self).execute(bs64, style)
        return execute_extract_data(request_json, self.RETURN_NAMES)


class SpeakerConversion(WorkerNode):
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required":
                {
                    "fileb": (DataType.BS64.name,),
                    "num": (DataType.INT.name, {"default": 0, "min": 0, "max": 0xffffffffffffffff}),
                }
        }

    RETURN_TYPES = (DataType.BYTES.name,)

    RETURN_NAMES = ("content",)

    CATEGORY = "worker"

    worker_cls = "SpeakerConversion"
    config = {
        "execute": "http://10.25.10.241:1148/wav2wav",
        "execute_kind": 4,
        "response_method": "content"
    }
    gearman_timeout: int = None
    request_timeout: int = None

    def execute(self, fileb, num):
        request_json = super(SpeakerConversion, self).execute(fileb, num)
        return execute_extract_data(request_json, self.RETURN_NAMES)
