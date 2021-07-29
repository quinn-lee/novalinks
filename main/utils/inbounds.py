import requests
from flask import current_app
from main.models import Waybill, TrackingInfo
import datetime


def inbound_query(inbound_num):
    waybill = Waybill.objects.raw({'w_no': inbound_num}).first()
    if waybill is not None:
        res = requests.get(
            "http://213.219.38.160:6001/api/v1.0/inbound_notifications/nova_show?inbound_num={}".format(
                inbound_num))
        if res.json().get('status') == "succ":
            wms_info = res.json().get('data')
            waybill.wms_user = wms_info.get('nickname')
            waybill.depot_status = wms_info.get('inbound_status')
            waybill.cont_num = wms_info.get('箱数')
            waybill.real_weight = wms_info.get('重量')
            waybill.container_num = wms_info.get('container_num')
            wms_info.pop('nickname')
            wms_info.pop('inbound_status')
            wms_info.pop('container_num')
            waybill.wms_info = wms_info
            waybill.save()
            if waybill.depot_status == 1:
                if TrackingInfo.objects.raw(
                        {'waybill': waybill._id, 'event': "货已入仓", 'location': "", 'description': ""}) \
                        .count() == 0:
                    tracking_info = TrackingInfo(waybill=waybill, event_time=datetime.datetime.now(),
                                                 event="货已入仓", location="", description="")
                    tracking_info.save()
            else:
                TrackingInfo.objects.raw(
                    {'waybill': waybill._id, 'event': "货已入仓", 'location': "", 'description': ""}).delete()