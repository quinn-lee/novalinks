# coding:utf8
from flask import Blueprint

# 创建蓝图对象
api = Blueprint("api_1_0", __name__)

# 导入蓝图视图
import main.api_1_0.session
import main.api_1_0.views
import main.api_1_0.orders

