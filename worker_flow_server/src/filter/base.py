class BaseFilter:
    def __init__(self):
        self.base_fields = ['status', 'updated_at', 'created_at']
        self.public_base_fields = []
        self.interface = ""

    def select_fun(self, fields=[], append=True):
        """
        :param fields:
        :param append: True 添加字段 False 移除字段
        :return:
        """
        if hasattr(self, self.interface):
            other_base_field, func_field = getattr(self, self.interface)()
            field = self.public_base_fields + other_base_field + self.base_fields

            if fields and append:
                return field + fields, func_field
            elif fields and not append:
                return list(set(field) - set(fields)), func_field
            else:
                return field, func_field
        else:
            return self.public_base_fields + self.base_fields, []
