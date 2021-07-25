import requests
from flask import current_app
from main.models import Waybill


def inbound_query(inbound_num):
    waybill = Waybill.objects.raw({'w_no': inbound_num}).first()
    if waybill is not None:
        res = requests.get(
            "http://213.219.38.160:6001/api/v1.0/inbound_notifications/nova_show?inbound_num={}".format(
                inbound_num))
        if res.json()['status'] == "succ":
            wms_info = res.json()['data']
            waybill.wms_user = wms_info['nickname']
            waybill.depot_status = wms_info['inbound_status']
            wms_info.pop('nickname')
            wms_info.pop('inbound_status')
            waybill.wms_info = wms_info
            waybill.save()
