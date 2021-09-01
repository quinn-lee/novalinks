# coding:utf-8
from main.api_1_0 import api
from flask import request, jsonify, current_app, session
from main.models import User, UserLog, Authorization
from werkzeug.security import generate_password_hash
from main.utils.response_code import RET
import re
import requests


@api.route("/users", methods=["GET"])
def users():
    """admin获取用户数据"""
    all_users = User.objects.all()
    data = [{'email': user.email, 'name': user.name} for user in all_users]
    data.insert(0, {'email': '', 'name': ''})
    current_app.logger.info(data)
    return jsonify(errno='0', data=data)


@api.route("/users/create", methods=["POST"])
def create_user():
    """admin创建用户
        参数： 用户名 邮箱 密码 密码确认 角色
        """
    # 获取参数
    current_app.logger.info("request_data: {}".format(request.get_data()))
    try:
        current_app.logger.info("request_json: {}".format(request.get_json()))
        req_dict = request.get_json()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.NOTJSON, errmsg="参数非Json格式")
    try:
        if req_dict is None:
            return jsonify(errno=RET.NOTJSON, errmsg="参数非Json格式")
        email = req_dict.get("email")
        password = req_dict.get("password")
        password_confirm = req_dict.get("password_confirm")
        name = req_dict.get("name")
        role = req_dict.get("role")
        nord_code = req_dict.get("nord_code")

        # 校验参数
        # 参数完整的校验
        if not all([email, password, password_confirm, name, role]):
            return jsonify(errno=RET.PARAMERR, errmsg="参数不完整")

        # 邮箱的格式
        if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            return jsonify(errno=RET.PARAMERR, errmsg="邮箱格式错误")

        # 密码与确认密码进行比对
        if password != password_confirm:
            current_app.logger.error(password)
            current_app.logger.error(password_confirm)
            return jsonify(errno=RET.DATAERR, errmsg="密码与确认密码不一致")
        if User.objects.raw({'email': email}).count() > 0:
            return jsonify(errno=RET.DATAERR, errmsg="email重复")
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.UNKOWNERR, errmsg=e)

    # 保存记录
    try:
        new = User(name=name, email=email, pwd=generate_password_hash(password), role=role, nord_code=nord_code)
        new.save()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmag="数据库异常")

    return jsonify(errno=RET.OK, errmsg="用户创建成功")


@api.route("/users/update", methods=["POST"])
def update_user():
    """admin修改用户
        参数： 用户名 邮箱 密码 密码确认 状态
        """
    # 获取参数
    current_app.logger.info("request_data: {}".format(request.get_data()))
    try:
        current_app.logger.info("request_json: {}".format(request.get_json()))
        req_dict = request.get_json()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.NOTJSON, errmsg="参数非Json格式")
    try:
        if req_dict is None:
            return jsonify(errno=RET.NOTJSON, errmsg="参数非Json格式")
        email = req_dict.get("email")
        password = req_dict.get("password")
        password_confirm = req_dict.get("password_confirm")
        name = req_dict.get("name")
        status = req_dict.get("status")
        role = req_dict.get("role")
        nord_code = req_dict.get("nord_code")

        # 校验参数
        # 参数完整的校验
        if not all([email, name, role, status]):
            return jsonify(errno=RET.PARAMERR, errmsg="参数不完整")

        user = User.objects.raw({'email': email}).first()
        if user is None:
            return jsonify(errno=RET.DATAERR, errmsg="用户不存在")
        # 密码与确认密码进行比对
        if password is not None and password != "":
            if password != password_confirm:
                current_app.logger.error(password)
                current_app.logger.error(password_confirm)
                return jsonify(errno=RET.DATAERR, errmsg="密码与确认密码不一致")
            else:
                user.pwd = generate_password_hash(password)
        if name is not None and name != "":
            user.name = name
        if nord_code is not None and nord_code != "":
            user.nord_code = nord_code
        if status is not None and status != "":
            user.status = status
        if role is not None and role != "":
            user.role = role

    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.UNKOWNERR, errmsg=e)

    # 保存记录
    try:
        user.save()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmag="数据库异常")

    return jsonify(errno=RET.OK, errmsg="用户修改成功")


@api.route("/users/index", methods=["POST"])
def query_users():
    """admin/inspector查询用户数据"""
    try:
        current_app.logger.info("request_json: {}".format(request.get_json()))
        req_dict = request.get_json()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.NOTJSON, errmsg="参数非Json格式")
    users = User.objects.raw({'role': {'$ne': 'admin'}})
    current_email = session.get("email")
    if current_email is None:
        return jsonify(errno=RET.SESSIONERR, errmsg="当前用户登录过期，请重新登录！")
    user = User.objects.raw({'email': current_email}).first()
    if user is None:
        return jsonify(errno=RET.SESSIONERR, errmsg="当前用户登录过期，请重新登录！")
    if user.role == "inspector":
        auths = Authorization.objects.raw({'from_user': user._id, 'status': 1})
        users = users.raw({'_id': {'$in': [auth.to_user._id for auth in auths]}})
    if req_dict is not None:
        if req_dict.get('email') is not None and req_dict.get('email') != '':
            users = users.raw({'email': req_dict.get('email')})
        if req_dict.get('role') is not None and req_dict.get('role') != '':
            users = users.raw({'role': req_dict.get('role')})
    data = [user.to_json() for user in users]
    current_app.logger.info(data)
    return jsonify(errno='0', data=data)


@api.route("/users/wms_inventories", methods=["GET"])
def wms_inventories():
    """admin/inspector查询库存数据"""
    nord_code = request.args.get('nord_code')
    sku_code = request.args.get('sku_code')
    barcode = request.args.get('barcode')
    res = requests.get(
        "http://213.219.38.160:6001/api/v1.0/inventories/nova_inventories?abbr_code={}&sku_code={}&barcode={}".format(
            nord_code, sku_code, barcode))
    if res.json().get('status') == "succ":
        return jsonify(errno='0', data=res.json().get('data'), totalRows=len(res.json().get('data')))
    else:
        return jsonify(errno=RET.REQERR, errmsg="请求数据错误")


@api.route("/users/wms_packs_inventories", methods=["GET"])
def wms_packs_inventories():
    """admin/inspector查询库存数据"""
    nord_code = request.args.get('nord_code')
    res = requests.get(
        "http://213.219.38.160:6001/api/v1.0/inbound_packs/nova_inventory?abbr_code={}".format(
            nord_code))
    if res.json().get('status') == "succ":
        return jsonify(errno='0', data=res.json().get('data'), totalRows=len(res.json().get('data')))
    else:
        return jsonify(errno=RET.REQERR, errmsg="请求数据错误")


@api.route("/users/wms_packs_inventory_skus", methods=["GET"])
def wms_packs_inventory_skus():
    """admin/inspector查询库存数据"""
    nord_code = request.args.get('nord_code')
    res = requests.get(
        "http://213.219.38.160:6001/api/v1.0/inbound_packs/nova_sku_inventory?abbr_code={}".format(
            nord_code))
    if res.json().get('status') == "succ":
        return jsonify(errno='0', data=res.json().get('data'), totalRows=len(res.json().get('data')))
    else:
        return jsonify(errno=RET.REQERR, errmsg="请求数据错误")


@api.route("/users/wms_spec_summary", methods=["GET"])
def wms_spec_summary():
    """admin/inspector查询库存数据"""
    nord_code = request.args.get('nord_code')
    res = requests.get(
        "http://213.219.38.160:6001/api/v1.0/inbound_parcels/nova_spec_summary?abbr_code={}".format(
            nord_code))
    if res.json().get('status') == "succ":
        return jsonify(errno='0', data=res.json().get('data'), totalRows=len(res.json().get('data')))
    else:
        return jsonify(errno=RET.REQERR, errmsg="请求数据错误")
