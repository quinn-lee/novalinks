# coding:utf-8

from main.api_1_0 import api
from flask import request, jsonify, current_app, session
from main.models import User, Authorization, Waybill, Depot
from main.utils.response_code import RET
from bson import ObjectId


@api.route("/waybill_create", methods=["POST"])
def waybill_create():
    """operator 创建运单
        参数： w_no, seller_email, depot_id
        """
    # 获取参数
    current_app.logger.info("request_data: {}".format(request.get_data()))
    try:
        current_app.logger.info("request_json: {}".format(request.get_json()))
        req_dict = request.get_json()
    except Exception as e:
        current_app.logger.info(e)
        return jsonify(errno=RET.NOTJSON, errmsg="参数非Json格式")
    if req_dict is None:
        return jsonify(errno=RET.NOTJSON, errmsg="参数非Json格式")
    seller_email = req_dict.get("seller_email")
    w_no = req_dict.get('w_no')
    depot_id = req_dict.get('depot_id')

    # 校验参数
    # 参数完整的校验
    if not all([seller_email, w_no, depot_id]):
        return jsonify(errno=RET.PARAMERR, errmsg="参数不完整")

    seller = User.objects.raw({'email': seller_email}).first()
    if seller is None:
        return jsonify(errno=RET.PARAMERR, errmsg="用户不存在")
    current_email = session.get("email")
    if current_email is None:
        return jsonify(errno=RET.SESSIONERR, errmsg="当前用户登录过期，请重新登录！")
    operator = User.objects.raw({'email': current_email}).first()
    if operator is None:
        return jsonify(errno=RET.SESSIONERR, errmsg="当前用户登录过期，请重新登录！")

    if Authorization.objects.raw({'from_user': operator._id, 'to_user': seller._id, 'status': 1}).count() == 0:
        return jsonify(errno=RET.PARAMERR, errmsg="授权记录已删除，您无权登记该用户的运单！")

    depot = Depot.objects.raw({'_id': ObjectId(depot_id)}).first()
    if depot is None:
        return jsonify(errno=RET.PARAMERR, errmsg="仓库不存在")

    if Waybill.objects.raw({'w_no': w_no}).count() > 0:
        return jsonify(errno=RET.PARAMERR, errmsg="该运单号（预报号）已存在")

    # 保存记录
    try:
        waybill = Waybill(w_no=w_no, seller=seller, operator=operator, depot=depot)
        waybill.save()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmag="数据库异常")

    return jsonify(errno=RET.OK, errmsg="运单创建成功")
