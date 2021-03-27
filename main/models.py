# coding:utf-8
import datetime
from werkzeug.security import check_password_hash
from pymodm import connect, fields, MongoModel, EmbeddedMongoModel
from pymongo.operations import IndexModel

connect('mongodb://localhost:27017/novaLinksDB')


# 用户
class User(MongoModel):
    email = fields.EmailField(required=True)  # 邮箱
    name = fields.CharField(required=True)  # 昵称
    pwd = fields.CharField(required=True)  # 密码，加密

    refresh_token = fields.CharField()  # refresh token
    lwa_app_id = fields.CharField()  # Client-ID
    lwa_client_secret = fields.CharField()  # Client-SECRET

    add_time = fields.DateTimeField(default=datetime.datetime.now)  # 添加时间

    class Meta:
        indexes = [
            IndexModel([('email', 1)], unique=True)
        ]

    def __repr__(self):  # 查询的时候返回
        return "<User %r>" % self.name

    def check_password(self, passwd):
        """
        检验密码正确性
        :param passwd:  用户登录时填写的原始密码
        :return:  如果正确返回True 否则返回 False
        """
        return check_password_hash(self.pwd, passwd)


# 登录日志
class UserLog(MongoModel):
    user = fields.ReferenceField(User)  # 所属用户
    ip = fields.CharField()  # 登录IP
    login_time = fields.DateTimeField(default=datetime.datetime.now)  # 登录时间

    def __repr__(self):
        return "<Userlog %r>" % self.user.name
