# coding:utf-8
from . import api
from flask import request, jsonify, current_app, session
from main.models import User, UserLog, Authorization
from werkzeug.security import generate_password_hash
from main.utils.response_code import RET
import re


@api.route("/sessions", methods=["POST"])
def login():
    """用户登录
    参数： 邮箱 密码 json
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

    # 校验参数
    # 参数完整的校验
    if not all([email, password]):
        return jsonify(errno=RET.PARAMERR, errmsg="参数不完整")

    # 邮箱的格式
    if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
        return jsonify(errno=RET.PARAMERR, errmsg="邮箱格式错误")

    user_ip = request.remote_addr  # 用户的ip地址

    # 从数据库中根据邮箱,查询用户的数据对象
    try:
        user = User.objects.raw({'email': email}).first()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="获取用户信息失败")

    # 用数据库的密码与用户填写的密码进行对比验证
    if user is None or not user.check_password(password):
        current_app.logger.error(password)
        return jsonify(errno=RET.DATAERR, errmsg="用户名或密码错误")

    if user.status != 0:
        return jsonify(errno=RET.DATAERR, errmsg="该用户已停用，不能登录")

    # 保存登录记录
    try:
        UserLog(user=user, ip=user_ip).save()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmag="数据库异常")

    # 如果验证相同成功,保存登录状态, 在 session中
    session["name"] = user.name
    session["email"] = user.email
    session["nord_code"] = user.nord_code

    return jsonify(errno=RET.OK, errmsg="登录成功", data=user.role)


@api.route("/session", methods=["GET"])
def check_login():
    """检查登录状态"""
    # 尝试从session中获取用户的名字
    name = session.get("name")
    nord_code = session.get("nord_code")
    current_app.logger.error("check_login --{}".format(session.get("email")))
    # 如果session中数据name名字存在,则表示用户已登录,则未登录
    if name is not None:
        return jsonify(errno=RET.OK, errmsg="true", data={"name": name, "nord_code": nord_code})
    else:
        return jsonify(errno=RET.SESSIONERR, errmsg="false")


@api.route("/session", methods=["DELETE"])
def logout():
    """登出"""
    # 清除session数据
    csrf_token = session.get("csrf_token")
    session.clear()
    session["csrf_token"] = csrf_token
    return jsonify(errno=RET.OK, errmsg="OK")
