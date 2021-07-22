# coding:utf-8

from main.api_1_0 import api
from flask import request, jsonify, current_app, session
from main.models import User, Authorization
from main.utils.response_code import RET
from bson import ObjectId
from datetime import datetime


@api.route("/seller_authorization_requests", methods=["GET"])
def seller_authorization_requests():
    """seller 查询请求授权的数据"""
    current_email = session.get("email")
    if current_email is None:
        return jsonify(errno=RET.SESSIONERR, errmsg="当前用户登录过期，请重新登录！")
    to_user = User.objects.raw({'email': current_email}).first()
    if to_user is None:
        return jsonify(errno=RET.SESSIONERR, errmsg="当前用户登录过期，请重新登录！")
    auths = Authorization.objects.raw({'to_user': to_user._id})

    data = [auth.to_seller_json() for auth in auths]
    current_app.logger.info(data)
    return jsonify(errno='0', data=data)


@api.route("/authorizations/pending_requests", methods=["GET"])
def pending_requests():
    """seller 查询待处理请求授权的数据"""
    current_email = session.get("email")
    if current_email is None:
        return jsonify(errno=RET.SESSIONERR, errmsg="当前用户登录过期，请重新登录！")
    to_user = User.objects.raw({'email': current_email}).first()
    if to_user is None:
        return jsonify(errno=RET.SESSIONERR, errmsg="当前用户登录过期，请重新登录！")
    auths = Authorization.objects.raw({'to_user': to_user._id, 'status': 0})

    data = [auth.to_seller_json() for auth in auths]
    current_app.logger.info(data)
    return jsonify(errno='0', data=data)


@api.route("/authorizations/processing", methods=["GET"])
def processing():
    """处理授权
    参数： id, status
    """
    auth = Authorization.objects.raw({'_id': ObjectId(request.args.get('id'))}).first()
    if auth is None:
        return jsonify(errno=RET.PARAMERR, errmsg="授权不存在")
    # 保存记录
    try:
        auth.status = int(request.args.get('status'))
        auth.processing_time = datetime.now()
        auth.save()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmag="数据库异常")
    return jsonify(errno="0", errmsg="授权处理成功")
