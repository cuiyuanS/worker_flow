from typing import Any, Dict, Type, Optional, get_type_hints, List

from pydantic import BaseModel, model_validator, ConfigDict, ValidationError
from pydantic_core import ErrorDetails

CUSTOM_MESSAGES = {
    'int_parsing': '不是合法整数',
    'float_parsing': '不是合法浮点数',
    'string_too_short': "字符串最小长度为{min_length}",
    "string_too_long": "字符串最大长度为{max_length}"
}


def convert_errors(e: ValidationError) -> List[ErrorDetails]:
    new_errors: List[ErrorDetails] = []
    for error in e.errors():
        custom_message = CUSTOM_MESSAGES.get(error['type'])
        if custom_message:
            ctx = error.get('ctx')
            error['msg'] = (
                custom_message.format(**ctx) if ctx else custom_message
            )
        new_errors.append(error)
    return new_errors


class BaseSchema(BaseModel):
    # 保护属性
    __model__ = None
    __context__ = {}
    model_config = ConfigDict()

    # validate_assignment=True 每次赋值数据都会走验证方法

    @classmethod
    def unvalidated(cls: "Type[BaseModel]", **data: Dict) -> "BaseModel":
        # 免验证  类似 棉花糖 load
        new_data = {}
        for name, field in cls.model_fields.items():
            if name in data:
                new_data[name] = data[name]
            # try:
            #     new_data[name] = data[name] if "name" in data else None
            # except KeyError:
            #     if field.is_required():
            #         raise TypeError(f"Missing required keyword argument {name!r}")
            #     if field.default is None:
            #         # deepcopy is quite slow on None
            #         value = None
            #     else:
            #         value = deepcopy(field.default)
            #     data[name] = value
        self = cls.__new__(cls)
        object.__setattr__(self, "__dict__", new_data)
        object.__setattr__(self, "__pydantic_fields_set__", set(new_data.keys()))
        object.__setattr__(self, "__pydantic_extra__", None)
        return self

    @model_validator(mode='before')
    @classmethod
    def convert_id(cls, data: Dict) -> Any:
        # 转换id
        id_field_value = data.pop("id", 0)
        if id_field_value:
            data[cls.__model__.meta["id_field"]] = id_field_value
        return data

    async def make_object(self):
        if self.__model__:
            self.__context__["data"] = {}
            annotations = get_type_hints(self.__model__)
            for key, value in annotations.items():
                if hasattr(self, key):
                    self.__context__["data"][key] = getattr(self, key)
            if getattr(self, self.__model__.meta["id_field"], 0):
                self.__context__["model_id"] = getattr(self, self.__model__.meta["id_field"])
                self.__context__["obj"] = await self.__model__.id_query_first(self.__context__["model_id"])
                if not self.__context__["obj"]:
                    raise ValueError("该数据记录不存在 请检查 id 属性")
            else:
                self.__context__["obj"] = self.__model__(**self.__context__["data"])

    async def save_object(self):
        if self.__model__:
            # 保存和更新
            if getattr(self, self.__model__.meta["id_field"], 0):
                self.__context__["data"].pop("created_at")
                self.__context__["obj"] = await self.__context__["obj"].update(**self.__context__["data"])
            else:
                self.__context__["obj"] = await self.__context__["obj"].insert()
            setattr(self, self.__model__.meta["id_field"],
                    getattr(self.__context__["obj"], self.__model__.meta["id_field"], 0))
            self.created_at = self.__context__["obj"].created_at
            self.status = self.__context__["obj"].status
            self.updated_at = self.__context__["obj"].updated_at
