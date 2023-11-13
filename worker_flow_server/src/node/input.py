from src.node.constant import DataType


class String:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required":
                {
                    "string": (DataType.STRING.name, {"default": ""})
                }
        }

    RETURN_TYPES = (DataType.STRING.name,)

    CATEGORY = "input"

    def execute(self, string):
        return str(string)


class Integer:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required":
                {
                    "integer": (DataType.INT.name, {"default": 0, "min": 0, "max": 0xffffffffffffffff})
                }
        }

    RETURN_TYPES = (DataType.INT.name,)

    CATEGORY = "input"

    def execute(self, integer):
        return int(integer)


class CdnPath:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required":
                {
                    "cdn_path": (DataType.CDN_PATH.name, {
                        "default": "http://10.25.20.15:8021/face_image/202310/12/01HCHV6EBKB236769QT1M68JPM.jpg"})
                }
        }

    RETURN_TYPES = (DataType.CDN_PATH.name,)

    CATEGORY = "input"

    def execute(self, cdn_path):
        return cdn_path,
