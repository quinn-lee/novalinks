# coding:utf-8

from main.api_1_0 import api
from flask import jsonify, current_app
from main.models import Depot


@api.route("/query_depots", methods=["GET"])
def query_depots():
    """查询仓库信息"""
    depots = Depot.objects.raw({'is_use': True})
    data = [depot.to_json() for depot in depots]
    data.insert(0, {'id': '', 'name': '', 'code': ''})
    current_app.logger.info(data)
    return jsonify(errno='0', data=data)
