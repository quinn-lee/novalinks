# coding:utf-8

from .. import api
from flask import request, jsonify, current_app, session
from main.models import User, Authorization
from main.utils.response_code import RET


@api.route("/query_unauthorized_users", methods=["GET"])
def query_unauthorized_users():
    """operator 查询未经自己授权的用户"""
    users = User.objects.raw({'role': 'seller'})
    current_email = session.get("email")
    if current_email is None:
        return jsonify(errno=RET.SESSIONERR, errmsg="当前用户登录过期，请重新登录！")
    from_user = User.objects.raw({'email': current_email}).first()
    if from_user is None:
        return jsonify(errno=RET.SESSIONERR, errmsg="当前用户登录过期，请重新登录！")
    auths = Authorization.objects.raw({'from_user': from_user._id, 'status': {'$ne': 2}})
    users = users.raw({'_id': {'$nin': [auth.to_user._id for auth in auths]}})
    data = [{'email': user.email, 'name': user.name} for user in users]
    data.insert(0, {'email': '', 'name': ''})
    current_app.logger.info(data)
    return jsonify(errno='0', data=data)


@api.route("/query_authorization_requests", methods=["GET"])
def query_authorization_requests():
    """operator 查询请求授权过的用户"""
    current_email = session.get("email")
    if current_email is None:
        return jsonify(errno=RET.SESSIONERR, errmsg="当前用户登录过期，请重新登录！")
    from_user = User.objects.raw({'email': current_email}).first()
    if from_user is None:
        return jsonify(errno=RET.SESSIONERR, errmsg="当前用户登录过期，请重新登录！")
    auths = Authorization.objects.raw({'from_user': from_user._id})

    data = [auth.to_json() for auth in auths]
    current_app.logger.info(data)
    return jsonify(errno='0', data=data)


@api.route("/authorization_request", methods=["POST"])
def authorization_request():
    """operator 请求授权
        参数： email
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

    # 校验参数
    # 参数完整的校验
    if not all([email]):
        return jsonify(errno=RET.PARAMERR, errmsg="参数不完整")

    to_user = User.objects.raw({'email': email}).first()
    if to_user is None:
        return jsonify(errno=RET.PARAMERR, errmsg="用户不存在")
    current_email = session.get("email")
    if current_email is None:
        return jsonify(errno=RET.SESSIONERR, errmsg="当前用户登录过期，请重新登录！")
    from_user = User.objects.raw({'email': current_email}).first()
    if from_user is None:
        return jsonify(errno=RET.SESSIONERR, errmsg="当前用户登录过期，请重新登录！")

    if Authorization.objects.raw({'from_user': from_user._id, 'to_user': to_user._id, 'status': {'$ne': 2}}).count() > 0:
        return jsonify(errno=RET.PARAMERR, errmsg="该用户已有授权请求记录，不能重复请求授权！")

    # 保存记录
    try:
        auth = Authorization(from_user=from_user, to_user=to_user, status=0)
        auth.save()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmag="数据库异常")

    return jsonify(errno=RET.OK, errmsg="授权请求已发送，等待卖家处理")
