# coding:utf-8
from main.api_1_0 import api
from flask import request, jsonify, current_app, session
from main.models import User, UserLog, Authorization
from werkzeug.security import generate_password_hash
from main.utils.response_code import RET
import re


@api.route("/users", methods=["GET"])
def users():
    """admin获取用户数据"""
    all_users = User.objects.all()
    data = [{'email': user.email, 'name': user.name} for user in all_users]
    data.insert(0, {'email': '', 'name': ''})
    current_app.logger.info(data)
    return jsonify(errno='0', data=data)


@api.route("/create_user", methods=["POST"])
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
        current_app.logger.info(e)
        return jsonify(errno=RET.NOTJSON, errmsg="参数非Json格式")
    if req_dict is None:
        return jsonify(errno=RET.NOTJSON, errmsg="参数非Json格式")
    email = req_dict.get("email")
    password = req_dict.get("password")
    password_confirm = req_dict.get("password_confirm")
    name = req_dict.get("name")
    role = req_dict.get("role")


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

    # 保存记录
    try:
        new = User(name=name, email=email, pwd=generate_password_hash(password), role=role)
        new.save()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmag="数据库异常")

    return jsonify(errno=RET.OK, errmsg="用户创建成功")


@api.route("/query_users", methods=["POST"])
def query_users():
    """admin/inspector查询用户数据"""
    try:
        current_app.logger.info("request_json: {}".format(request.get_json()))
        req_dict = request.get_json()
    except Exception as e:
        current_app.logger.info(e)
        return jsonify(errno=RET.NOTJSON, errmsg="参数非Json格式")
    users = User.objects.raw({'role': {'$ne': 'admin'}})
    if req_dict is not None:
        if req_dict.get('email') is not None and req_dict.get('email') != '':
            users = users.raw({'email': req_dict.get('email')})
        if req_dict.get('role') is not None and req_dict.get('role') != '':
            users = users.raw({'role': req_dict.get('role')})
    data = [user.to_json() for user in users]
    current_app.logger.info(data)
    return jsonify(errno='0', data=data)
