import src.config.base as base_config


class Connection:
    def __init__(self, collect_name, session=None):
        from src import mongodb_client
        self.collection = mongodb_client[base_config.MONGODB_DB][collect_name]
        self.session = session

    async def insert(self, item):
        """
        插入数据
        :param item: dict
        :return: 插入返回的ObjectId
        """
        res = await self.collection.insert_one(item, session=self.session)
        return res.inserted_id

    async def update(self, condition, update_dict):
        """
        更新數據
        :param condition: 条件
        :param update_dict: 更新的数据
        :return:
        """
        obj = await self.collection.update_many(condition, {'$set': update_dict},session=self.session)
        return obj.matched_count > 0 # 如果有匹配的记录并且没有异常则说明成功。

    async def delete(self, condition):
        """
        刪除數據
        :param condition: 条件
        :return:
        """
        return await self.collection.delete_many(condition,session=self.session)

    async def drop(self):
        """
        删除集合
        :return:
        """
        return await self.collection.drop()

    async def count(self, condition):
        """
        查询数量
        :param condition: 条件
        :return:
        """
        return await self.collection.count_documents(condition, session=self.session)

    async def fetchone_to_dict(self, condition, projection={}, sort=[]):
        """
        查询单条
        :param projection:  {'_id':0,'timestamp':0} 使用0或1，来表示不显示或显示指定字段  除’_id’以外，不能在一个对象中同时指定 0 和 1，如果你设置了一个字段为 0，则其他都为 1，反之亦然。
        :param condition: 条件
        :param sort: [('name', 1), ("_id", -1)]
        :return:
        """
        return await self.collection.find_one(condition, projection=projection, sort=sort, session=self.session)

    async def fetch_to_page(self, condition, page_num, page_size, projection={}, sort=[]):
        """
        分页查询
        :param projection: 字段显示或者隐藏
        :param condition: 条件
        :param page_num: 页数
        :param page_size: 大小
        :param sort: [('name', -1), ("_id", -1)]
        :return:
        """
        items_skipped = (page_num - 1) * page_size
        cursor = self.collection.find(condition, projection=projection, session=self.session).skip(items_skipped)
        # 将上述查询通过Python 转换为 mongodb 的查询语句
        if len(sort) > 0:
            cursor = cursor.sort(sort).limit(page_size)
        else:
            cursor = cursor.limit(page_size)
        items = await cursor.to_list(page_size)
        # items = [await i for i in cursor]
        return items

    async def fetchall_to_list(self, condition, projection={}, sort=[]):
        """
        查询多条
        :param projection: 字段显示或者隐藏
        :param condition:  条件
        :param sort: [('name', 1), ("_id", -1)]
        :return:
        """
        cursor = self.collection.find(condition, projection=projection, sort=sort, session=self.session)
        # items = [i for i in cursor]
        items = await cursor.to_list(None)
        return items

    async def fetch_aggregate(self, pipeline):
        """
        聚合查询
        :param pipeline: 聚合条件
        :return:
        """
        cursor = self.collection.aggregate(pipeline, session=self.session)
        # items = [i for i in cursor]
        items = await cursor.to_list(None)
        return items

    async def find_one_and_update(self, condition, update):
        """
        自增id 表专用 不使用事务
        :param condition: 约束条件
        :param update: 更新
        :return:
        """
        return await self.collection.find_one_and_update(condition, update, upsert=True)
