from enum import Enum


class DataType(Enum):
    # base
    INT = 1
    STRING = 2
    BYTES = 3
    # extra
    BS64 = 21
    LOCAL_PATH = 22
    CDN_PATH = 23
    JSON = 24


AIGenModel_Sex = [0, 1, 2]

from src.node.worker import *
from src.node.tool import *
from src.node.output import *
from src.node.input import *

NODE_CLASS_MAPPINGS = {
    # worker
    "AIGenModelFFHQFlame": AIGenModelFFHQFlame,
    "MixEye": MixEye,
    "U3DFlameFFHQ": U3DFlameFFHQ,
    "SpeakerConversion": SpeakerConversion,
    "VideoStylization": VideoStylization,
    # tool
    "UploadLocal": UploadLocal,
    "Bs64ConvertBytes": Bs64ConvertBytes,
    "BytesConvertBs64": BytesConvertBs64,
    "UploadBytes": UploadBytes,
    # "HttpRequestPost": HttpRequestPost,
    # "HttpRequestGet": HttpRequestGet,
    "CdnConvertBytes": CdnConvertBytes,
    # input
    # "String": String,
    # "Integer": Integer,
    "CdnPath": CdnPath,
    # output
    "ModelFFHQFlameOutPut": ModelFFHQFlameOutPut,
    "VideoStylizationOutPut": VideoStylizationOutPut,
    "SpeakerConversionOutPut": SpeakerConversionOutPut
}

NODE_DISPLAY_NAME_MAPPINGS = {
    # worker
    "AIGenModelFFHQFlame": "AIGenModelFFHQFlame",
    "U3DFlameFFHQ": "U3DFlameFFHQ",
    # tool
    "Upload": "Upload",
    "HttpRequestPost": "HttpRequestPost",
    "HttpRequestGet": "HttpRequestGet",
    # output
    "ModelFFHQFlameOutPut": "ModelFFHQFlameOutPut"
}

