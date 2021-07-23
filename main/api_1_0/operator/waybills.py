# coding:utf-8

from main.api_1_0 import api
from flask import request, jsonify, current_app, session
from main.models import User, Authorization, Waybill, Depot
from main.utils.response_code import RET
from bson import ObjectId
from werkzeug.utils import secure_filename
import datetime


@api.route("/waybills/edit", methods=["GET"])
def waybill_edit():
    waybill = Waybill.objects.raw({'_id': ObjectId(request.args.get('id'))}).first()
    if waybill is None:
        return jsonify(errno=RET.DBERR, errmsg="运单不存在！")

    return jsonify(errno=RET.OK, data=waybill.to_json())


@api.route("/waybills/show_billing", methods=["GET"])
def show_billing():
    waybill = Waybill.objects.raw({'_id': ObjectId(request.args.get('id'))}).first()
    if waybill is None:
        return jsonify(errno=RET.DBERR, errmsg="运单不存在！")
    if waybill.lading_bill is None:
        return jsonify(errno=RET.DBERR, errmsg="运单的提单文件不存在！")

    f = waybill.lading_bill.file
    url = "/files/lading_bills/{}.{}".format(str(waybill._id), waybill.lading_bill_ext())
    with open("main/static/html{}".format(url), 'wb') as file:
        file.write(f.read())

    return jsonify(errno=RET.OK, data=url)


@api.route("/waybills/delete_billing", methods=["GET"])
def delete_billing():
    waybill = Waybill.objects.raw({'_id': ObjectId(request.args.get('id'))}).first()
    if waybill is None:
        return jsonify(errno=RET.DBERR, errmsg="运单不存在！")

    try:
        waybill.lading_bill = None
        waybill.lading_bill_name = None

        waybill.save()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmag="数据库异常")

    return jsonify(errno=RET.OK)


@api.route("/waybills/delete", methods=["GET"])
def delete_waybill():
    waybill = Waybill.objects.raw({'_id': ObjectId(request.args.get('id'))}).first()

    try:
        if waybill is not None:
            waybill.delete()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmag="数据库异常")

    return jsonify(errno=RET.OK)


@api.route("/waybills/operator/index", methods=["GET"])
def waybill_index():
    current_email = session.get("email")
    if current_email is None:
        return jsonify(errno=RET.SESSIONERR, errmsg="当前用户登录过期，请重新登录！")
    operator = User.objects.raw({'email': current_email}).first()
    if operator is None:
        return jsonify(errno=RET.SESSIONERR, errmsg="当前用户登录过期，请重新登录！")

    waybills = Waybill.objects.raw({'operator': operator._id})
    if request.args.get('w_no') is not None and request.args.get('w_no') != '':
        waybills = waybills.raw({'w_no': request.args.get('w_no')})
    if request.args.get('customs_apply') is not None and request.args.get('customs_apply') != '':
        waybills = waybills.raw({'customs_apply': request.args.get('customs_apply')})
    if request.args.get('customs_declaration') is not None and request.args.get('customs_declaration') != '':
        waybills = waybills.raw({'customs_declaration': request.args.get('customs_declaration')})
    if request.args.get('depot_status') is not None and request.args.get('depot_status') != '':
        waybills = waybills.raw({'depot_status': request.args.get('depot_status')})

    return jsonify(errno=RET.OK, data=[waybill.to_json() for waybill in waybills], totalRows=waybills.count())


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


@api.route("/waybills/update", methods=["POST"])
def waybill_update():
    """operator 修改运单
        参数： w_no, seller_email, depot_id
        """
    # 获取参数
    billing_weight = request.form.get('billing_weight')
    customs_apply = request.form.get('customs_apply')
    delivery_time = request.form.get('delivery_time')
    customs_declaration = request.form.get('customs_declaration')
    etd = request.form.get('etd')
    eta = request.form.get('eta')
    waybill_id = request.form.get('id')
    agent_info = request.form.get('agent_info')

    if waybill_id is None or waybill_id == "":
        return jsonify(errno=RET.PARAMERR, errmsg="参数不正确！")

    waybill = Waybill.objects.raw({'_id': ObjectId(waybill_id)}).first()
    if waybill is None:
        return jsonify(errno=RET.DBERR, errmsg="运单不存在！")

    # 保存记录
    try:
        if delivery_time is not None and delivery_time != "":
            waybill.delivery_time = datetime.datetime.strptime(delivery_time, '%Y/%m/%d')
        else:
            waybill.delivery_time = None
        if etd is not None and etd != "":
            waybill.etd = datetime.datetime.strptime(etd, '%Y/%m/%d')
        else:
            waybill.etd = None
        if eta is not None and eta != "":
            waybill.eta = datetime.datetime.strptime(eta, '%Y/%m/%d')
        else:
            waybill.eta = None
        if billing_weight is not None and billing_weight != "":
            waybill.billing_weight = billing_weight
        else:
            waybill.billing_weight = None
        if customs_apply is not None and customs_apply != "":
            waybill.customs_apply = customs_apply
        else:
            waybill.customs_apply = None
        if customs_declaration is not None and customs_declaration != "":
            waybill.customs_declaration = customs_declaration
        else:
            waybill.customs_declaration = None
        if agent_info is not None and agent_info != "":
            waybill.agent_info = agent_info
        else:
            waybill.agent_info = None
        waybill.save()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmag="数据库异常")

    return jsonify(errno=RET.OK, errmsg="运单修改成功")


@api.route("/waybills/upload_lading_bill", methods=["POST"])
def waybill_upload_lading_bill():
    """operator 上传提单
        参数： w_no, lading_bill
        """
    # 获取参数
    waybill_id = request.form.get('id')

    lading_bill = request.files.get('lading_bill')

    if waybill_id is None or waybill_id == "":
        return jsonify(errno=RET.PARAMERR, errmsg="参数不正确！")

    waybill = Waybill.objects.raw({'_id': ObjectId(waybill_id)}).first()
    if waybill is None:
        return jsonify(errno=RET.DBERR, errmsg="运单不存在！")

    # 保存记录
    try:
        if lading_bill is not None:
            waybill.lading_bill = lading_bill
            waybill.lading_bill_name = secure_filename(lading_bill.filename)
        waybill.save()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmag="数据库异常")

    return jsonify(errno=RET.OK, errmsg="运单修改成功")
