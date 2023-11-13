import pickle

from src.lib.gearman.client import GearmanClient
from src.lib.gearman.worker import GearmanWorker
from src.lib.gearman import DataEncoder
import json


# worker cline 通信传输数据的序列化和反序列化
class JSONDataEncoder(DataEncoder):
    @classmethod
    def encode(cls, encode_object):
        try:
            data = json.dumps(encode_object)
        except:
            data = pickle.dumps(encode_object)
        return data


    @classmethod
    def decode(cls, decode_string):
        try:
            data = json.loads(decode_string.decode("utf-8"))
        except:
            data = pickle.loads(decode_string)
        return data


class PickleDataEncode(DataEncoder):
    @classmethod
    def encode(cls, encode_object):
        return pickle.dumps(encode_object)

    @classmethod
    def decode(cls, decode_string):
        # 反序列化对象存在失败情况
        try:
            return pickle.loads(decode_string)
        except Exception as e:
            return {"data": {"load_fail": True}}


class GearmanJsonClient(GearmanClient):
    data_encoder = JSONDataEncoder


class GearmanJsonWorker(GearmanWorker):
    data_encoder = JSONDataEncoder


class GearmanPickleClient(GearmanClient):
    data_encoder = PickleDataEncode


class GearmanPickleWorker(GearmanWorker):
    data_encoder = PickleDataEncode
