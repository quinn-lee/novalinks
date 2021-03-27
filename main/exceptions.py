# coding:utf-8


# 自定义异常类
class ValidationException(Exception):
    def __init__(self, code, msg):
        super().__init__(self)  # 初始化父类
        self.code = code
        self.msg = msg

    def __str__(self):
        return "{} {}".format(self.code, self.msg)
