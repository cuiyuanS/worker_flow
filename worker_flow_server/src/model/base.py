from datetime import datetime
from dataclasses import dataclass, asdict
from bson import ObjectId

from . import Connection
from src.middleware.global_ctx import g


@dataclass
class Base:
    meta = {
        "tablename": "",
    }

    # _id: ObjectId = ObjectId("000000000000000000000000")

    @classmethod
    def convert_field_id_to_id(cls, condition: dict):
        """
        转换 id 查询为 _id
        :param condition:
        :return:
        """
        if "id_field" in cls.meta and cls.meta["id_field"] in condition:
            d = {}
            for key, value in condition.items():
                if key == cls.meta["id_field"]:
                    d["_id"] = value
                else:
                    d[key] = value
            return d
        else:
            return condition

    @classmethod
    def connection(cls, use_transactional=None):
        if use_transactional == None:
            use_tr = cls.meta.get("use_transactional", True)
        else:
            use_tr = use_transactional
        if use_tr:
            return Connection(cls.meta["tablename"], session=g.session if hasattr(g, "session") else None)
        else:
            return Connection(cls.meta["tablename"])

    @classmethod
    async def query_page(cls, page_num=1, page_size=10, projection={}, sort=[], load=True, **condition):
        condition = cls.convert_field_id_to_id(condition)
        data = await cls.connection().fetch_to_page(condition, projection=projection, page_num=page_num, page_size=page_size,
                                              sort=sort)
        if not data:
            return []
        if load:
            return cls.load(data, many=True)
        else:
            return data

    @classmethod
    async def query_all(cls, load=True, projection={}, sort=[], **kwargs):
        kwargs = cls.convert_field_id_to_id(kwargs)
        data = await cls.connection().fetchall_to_list(kwargs, projection=projection, sort=sort)
        if not data:
            return []
        if load:
            return cls.load(data, many=True)
        else:
            return data

    @classmethod
    async def query_count(cls, **kwargs):
        kwargs = cls.convert_field_id_to_id(kwargs)
        return await cls.connection().count(kwargs)

    @classmethod
    async def query_first(cls, load=True, projection={}, sort=[], **kwargs):
        kwargs = cls.convert_field_id_to_id(kwargs)
        obj = await cls.connection().fetchone_to_dict(kwargs, projection=projection, sort=sort)
        if not obj:
            return None
        if load:
            return cls.load(obj)
        else:
            return obj

    @classmethod
    async def query_aggregate(cls, pipeline):
        return await cls.connection().fetch_aggregate(pipeline)

    @classmethod
    async def update_kwargs(cls, condition, use_transactional=None, **update_dict):
        condition = cls.convert_field_id_to_id(condition)
        return await cls.connection(use_transactional=use_transactional).update(condition, update_dict)

    async def insert(self, use_transactional=None):
        if "increase_key" in self.meta and self.meta["increase_key"] == True:
            inc_key = "%s_%s" % (self.meta["tablename"], "id")
            sequence = await Sequence.increment(inc_key)
            if sequence:
                setattr(self, self.meta["id_field"], sequence["val"] + 1)
            else:
                # setattr(self, self.meta["id_field"], 1)  todo
                raise Exception('自增表更新失败！')
            data = self.dump()
            data["_id"] = sequence["val"] + 1
        else:
            data = self.dump()
        connection = self.connection(use_transactional=use_transactional)
        new_id = await connection.insert(data)
        if not new_id:
            return {}
        else:
            return self.load(await connection.fetchone_to_dict({"_id": new_id}))

    @classmethod
    async def id_query_first(cls, id_val, load=True):
        return await cls.query_first(load=load, **{"_id": int(id_val)})

    @classmethod
    async def query_list(cls, page=1, per_page=100, load=False, projection=None, sort=[], **kwargs):
        if projection is None:
            projection = {'_id': 0}
        return await cls.query_page(page_num=page, page_size=per_page, load=load, projection=projection, sort=sort, **kwargs)

    async def update(self, use_transactional=None, **kwargs):
        if not kwargs:
            return
        if "_id" in kwargs: kwargs.pop("_id")
        condition = {"_id": getattr(self, self.meta["id_field"])}
        connection = self.connection(use_transactional=use_transactional)
        await connection.update(condition, kwargs)
        return self.load(await connection.fetchone_to_dict(condition))

    async def delete(self, use_transactional=None, **kwargs):
        increase_key = self.meta.get("increase_key", False)
        if increase_key:
            condition = {"_id": getattr(self, self.meta["id_field"])}
        else:
            condition = {"_id": ObjectId(getattr(self, self.meta["id_field"]))}
        return await self.connection(use_transactional=use_transactional).delete(condition)

    async def drop(self):
        return await self.connection().drop()

    def dump(self):
        return asdict(self)

    @classmethod
    def load(cls, data, many=False):
        if many:
            return [cls._load(i) for i in data]
        else:
            return cls._load(data)

    @classmethod
    def _load(cls, data):
        obj = cls()
        for key, value in data.items():
            obj.__setattr__(key, value)
        return obj


@dataclass
class Sequence(Base):
    meta = {
        "tablename": "sequence",
    }

    name: str = ""  # 名称
    val: int = 0

    @classmethod
    async def increment(cls, inc_key):
        condition = {"name": inc_key}
        t = await cls.connection().fetchone_to_dict(condition=condition)
        if not t:
            data = cls()
            data.name = inc_key
            await data.insert(use_transactional=False)
        update = {"$inc": {"val": 1}}
        res = await cls.connection().find_one_and_update(condition, update)
        return res


@dataclass
class FieldBase(Base):
    created_at: datetime = None
    updated_at: datetime = datetime.now()
    status: int = 1  # 状态 4:已删除

    async def insert(self, use_transactional=None):
        if not self.created_at:
            self.created_at = datetime.now()
        res = await super(FieldBase, self).insert()
        return res

    async def update(self, use_transactional=None, **kwargs):
        if not kwargs:
            return
        kwargs["updated_at"] = datetime.now()
        res = await super(FieldBase, self).update(**kwargs)
        return res

    @classmethod
    async def query_mark_delete(cls, ids=[]):
        """
        删除
        :param ids: id 数组
        :return:
        """
        res = await super(FieldBase, cls).update_kwargs({'_id': {'$in': ids}}, **{'status': 4})
        return res

    @classmethod
    async def query_mark_status(cls, id_value, status):
        """
        更新状态
        :param id_value: id值
        :param status: int
        :return:
        """
        res = await super(FieldBase, cls).update_kwargs({'_id': id_value}, **{'status': status})
        return res
