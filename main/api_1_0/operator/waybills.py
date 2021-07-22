# coding:utf-8

from main.api_1_0 import api
from flask import request, jsonify, current_app, session
from main.models import User, Authorization, Waybill, Depot
from main.utils.response_code import RET
from bson import ObjectId
from werkzeug.utils import secure_filename
import datetime


@api.route("/waybills/create", methods=["POST"])
def waybill_create():
    """operator 创建运单
        参数： w_no, seller_email, depot_id
        """
    # 获取参数
    seller_email = request.form.get("seller_email")
    w_no = request.form.get('w_no')
    depot_id = request.form.get('depot_id')
    lading_bill = request.files.get('lading_bill')
    billing_weight = request.form.get('billing_weight')
    customs_apply = request.form.get('customs_apply')
    delivery_time = request.form.get('delivery_time')
    customs_declaration = request.form.get('customs_declaration')
    etd = request.form.get('etd')
    eta = request.form.get('eta')

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
        if lading_bill is not None:
            waybill.lading_bill = lading_bill
            waybill.lading_bill_name = secure_filename(lading_bill.filename)
        if delivery_time is not None and delivery_time != "":
            waybill.delivery_time = datetime.datetime.strptime(delivery_time, '%Y/%m/%d')
        if etd is not None and etd != "":
            waybill.etd = datetime.datetime.strptime(etd, '%Y/%m/%d')
        if eta is not None and eta != "":
            waybill.eta = datetime.datetime.strptime(eta, '%Y/%m/%d')
        if billing_weight is not None and billing_weight != "":
            waybill.billing_weight = billing_weight
        if customs_apply is not None and customs_apply != "":
            waybill.customs_apply = customs_apply
        if customs_declaration is not None and customs_declaration != "":
            waybill.customs_declaration = customs_declaration
        waybill.save()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmag="数据库异常")

    return jsonify(errno=RET.OK, errmsg="运单创建成功")
