from . import api
from flask import jsonify, request, current_app
from main.utils.response_code import RET
from main.models import User, Order, OrderItem
from datetime import datetime


@api.route("/orders/statistics", methods=["POST"])
def statistics():
    """销量统计
    参数： 起始日期，终止日期，用户邮箱
    """
    try:
        current_app.logger.info("request_json: {}".format(request.get_json()))
        req_dict = request.get_json()
    except Exception as e:
        current_app.logger.info(e)
        return jsonify(errno=RET.NOTJSON, errmsg="参数非Json格式")
    if req_dict.get('email') is not None and req_dict.get('email') != '':
        users = User.objects.raw({'email': req_dict.get('email')})
    else:
        users = User.objects.all()
    data = []
    for user in users:
        orders = Order.objects.raw({'user': user._id,
                           'PurchaseDate': {'$gte': datetime.strptime(req_dict.get('start_date'), '%Y/%m/%d')},
                           'PurchaseDate': {'$lte': datetime.strptime(req_dict.get('end_date'), '%Y/%m/%d')}})
        if orders.count() > 0:
            asins = []
            for order in orders:
                asins.extend(order.asins())
            item_category_num = len(set(asins))
            sum_item_num = sum([order.item_num() for order in orders])
            sum_order_amount = round(sum([order.order_amount() for order in orders]), 2)
            avg_item_num_per_order = round((sum_item_num / orders.count()), 2)
            avg_order_amount = round((sum_order_amount / orders.count()), 2)
            data.append({'item_category_num': item_category_num, 'sum_item_num': sum_item_num,
                        'sum_order_amount': "%s EUR" % sum_order_amount,
                         'avg_item_num_per_order': avg_item_num_per_order,
                         'avg_order_amount': "%s EUR" % avg_order_amount,
                         'start_date': req_dict.get('start_date'), 'end_date': req_dict.get('end_date'),
                         'email': user.email, 'user_name': user.name})
    return jsonify(errno="0", data=data)


@api.route("/order/details", methods=["GET"])
def details():
    """订单详情
    参数： 起始日期，终止日期，用户邮箱
    """
    user = User.objects.raw({'email': request.args.get('email')}).first()
    orders = Order.objects.raw({'user': user._id,
                                'PurchaseDate': {'$gte': datetime.strptime(request.args.get('start_date'), '%Y/%m/%d')},
                                'PurchaseDate': {'$lte': datetime.strptime(request.args.get('end_date'), '%Y/%m/%d')}})
    data = [{'AmazonOrderId': order.AmazonOrderId,
             'PurchaseDate': order.PurchaseDate.strftime('%Y-%m-%d'),
             'order_amount': "%s EUR" % order.order_amount(),
             'item_category_num': len(order.order_items()),
             'item_num': order.item_num()} for order in orders]
    return jsonify(errno="0", data=data)
