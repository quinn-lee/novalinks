# coding:utf8
from flask import Blueprint

# 创建蓝图对象
api = Blueprint("api_1_0", __name__)

# 导入蓝图视图
import main.api_1_0.session
import main.api_1_0.views
import main.api_1_0.admin.orders
import main.api_1_0.admin.inventories
import main.api_1_0.admin.users
import main.api_1_0.operator.authorizations
import main.api_1_0.operator.waybills
import main.api_1_0.operator.depots
import main.api_1_0.seller.authorizations

