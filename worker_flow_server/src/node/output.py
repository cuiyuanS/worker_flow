import inspect

from src.node.constant import DataType


class Output:
    def execute(self, *args):
        data = {}
        params = inspect.signature(self.execute).parameters
        # 遍历参数并打印参数名
        for i, param_name in enumerate(list(params)):
            data[param_name] = args[i]
        return data,


class ModelFFHQFlameOutPut(Output):
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required":
                {
                    "texture_path": (DataType.CDN_PATH.name,),
                    "left_eye_path": (DataType.CDN_PATH.name,),
                    "right_eye_path": (DataType.CDN_PATH.name,),
                    "obj_file_path": (DataType.CDN_PATH.name,),
                    "obj_data_file_path": (DataType.CDN_PATH.name,),
                    "ModelPath": (DataType.CDN_PATH.name,),
                }
        }

    RETURN_TYPES = (DataType.JSON.name,)

    OUTPUT_NODE = True

    CATEGORY = "output"

    def execute(self, texture_path, left_eye_path, right_eye_path, obj_file_path, obj_data_file_path, ModelPath):
        return super(ModelFFHQFlameOutPut, self).execute(texture_path, left_eye_path, right_eye_path, obj_file_path, obj_data_file_path, ModelPath)


class VideoStylizationOutPut(Output):
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required":
                {
                    "video_path": (DataType.CDN_PATH.name,),
                    "image_path": (DataType.CDN_PATH.name,),
                }
        }

    RETURN_TYPES = (DataType.JSON.name,)

    OUTPUT_NODE = True

    CATEGORY = "output"

    def execute(self, video_path, image_path):
        return super(VideoStylizationOutPut, self).execute(video_path, image_path)


class SpeakerConversionOutPut(Output):
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required":
                {
                    "audio_path": (DataType.CDN_PATH.name,),
                }
        }

    RETURN_TYPES = (DataType.JSON.name,)

    OUTPUT_NODE = True

    CATEGORY = "output"

    def execute(self, audio_path):
        return super(SpeakerConversionOutPut, self).execute(audio_path)


