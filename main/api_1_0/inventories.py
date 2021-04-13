# coding:utf-8

from . import api
from flask import jsonify, request, current_app
from main.utils.response_code import RET
from main.models import Inventory, User


@api.route("/inventories", methods=["GET"])
def inventories():
    """sku详情
    参数： ASIN SKU
    """
    user = User.objects.first()
    invens = Inventory.objects.raw({'user': user._id})
    current_app.logger.info(request.args.get('asin'))
    current_app.logger.info(request.args.get('sku'))
    if request.args.get('asin') is not None and request.args.get('asin') != '':
        invens = invens.raw({'asin': request.args.get('asin')})
    if request.args.get('sku') is not None and request.args.get('sku') != '':
        invens = invens.raw({'sku': request.args.get('sku')})
    current_app.logger.info(invens.count())
    data = [inventory.to_json() for inventory in invens]
    return jsonify(errno="0", data=data, totalRows=invens.count())
