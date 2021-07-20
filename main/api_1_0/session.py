# coding:utf-8
from . import api
from flask import request, jsonify, current_app, session
from main.models import User, UserLog
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

    return jsonify(errno=RET.OK, errmsg="登录成功")


@api.route("/session", methods=["GET"])
def check_login():
    """检查登录状态"""
    # 尝试从session中获取用户的名字
    name = session.get("name")
    # 如果session中数据name名字存在,则表示用户已登录,则未登录
    if name is not None:
        return jsonify(errno=RET.OK, errmsg="true", data={"name": name})
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


@api.route("/users", methods=["GET"])
def users():
    """获取用户数据"""
    all_users = User.objects.all()
    data = [{'email': user.email, 'name': user.name} for user in all_users]
    data.insert(0, {'email': '', 'name': ''})
    current_app.logger.info(data)
    return jsonify(errno='0', data=data)


@api.route("/create_user", methods=["POST"])
def create_user():
    """创建用户
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
    """查询用户数据"""
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
    data = [{'email': user.email, 'name': user.name, 'role': user.role, 'status': {0: '正常', 1: '停用'}.get(user.status)}
            for user in users]
    current_app.logger.info(data)
    return jsonify(errno='0', data=data)
