# coding: utf-8

from werkzeug.routing import BaseConverter
import time
import hashlib
import http.client
import xlsxwriter
import sys
import importlib
from flask import current_app
importlib.reload(sys)


# 定义正则转换器
class ReConverter(BaseConverter):
    """"""
    def __init__(self, url_map, regex):
        # 调用父类的初始化方法
        super(ReConverter, self).__init__(url_map)
        # 保存正则表达式
        self.regex = regex


# 写入Excel文件
class Excel(object):
    # 初始化，设置文件名
    def __init__(self, name):
        self.book = xlsxwriter.Workbook(name)
        self.sheet = self.book.add_worksheet()

    # 写入列名
    def write_colume_name(self, colums_name):
        for i in range(0, len(colums_name)):
            self.sheet.write(0, i, colums_name[i])

    # 写入数据
    def write_content(self, row_num, data):
        for i in range(0, len(data)):
            self.sheet.write(row_num, i, data[i])

    # 关闭文件
    def close(self):
        self.book.close()


# 带token认证的post
def token_post(ip, port, method, data):
    conn = None
    try:
        from main.models import User
        user = User.query.first()
        ts = str(int(round(time.time() * 1000)))
        md5_code = hashlib.md5((str(user.uuid) + str(ts) + str(user.api_key)).encode("utf-8")).hexdigest()
        print(md5_code)
        headers = {"Content-type": "application/json",
                   "Authorization": "Token {}&{}&{}".format(user.uuid, ts, md5_code)}
        conn = http.client.HTTPConnection(ip, port, timeout=200)
        conn.request("POST", method, data, headers)
        response = conn.getresponse()
        retmsg = response.read().decode("utf8")
        conn.close()
        return retmsg
    except Exception as e:
        print(e)
    finally:
        if conn:
            conn.close()


# 普通post
def common_post(ip, port, method, data):
    conn = None
    try:
        headers = {"Content-type": "application/json"}
        conn = http.client.HTTPConnection(ip, port, timeout=200)
        conn.request("POST", method, data, headers)
        response = conn.getresponse()
        current_app.logger.info("response={}".format(response))
        retmsg = response.read().decode("utf8")
        current_app.logger.info("retmsg={}".format(retmsg))
        conn.close()
        return retmsg
    except Exception as e:
        print(e)
    finally:
        if conn:
            conn.close()
