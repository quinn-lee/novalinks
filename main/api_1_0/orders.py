from . import api
from flask import jsonify, request, current_app
from main.utils.response_code import RET


@api.route("/orders/statistics", methods=["POST"])
def statistics():
    """销量统计
    参数： 起始日期，终止日期
    """
    try:
        current_app.logger.info("request_json: {}".format(request.get_json()))
        req_dict = request.get_json()
    except Exception as e:
        current_app.logger.info(e)
        return jsonify(errno=RET.NOTJSON, errmsg="参数非Json格式")
    data = [{'item_category_num': 1, 'sum_item_num': 2, 'sum_order_amount': 3, 'avg_item_num_per_order': 4,
             'avg_order_amount': 5, 'start_date': req_dict.get('start_date'),
             'end_date': req_dict.get('end_date')}]
    return jsonify(errno="0", data=data)
