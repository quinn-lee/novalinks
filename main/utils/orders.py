from flask import current_app
from sp_api.api import Orders
from sp_api.base import SellingApiException, Marketplaces
from datetime import datetime, timedelta
from main.models import Order, OrderItem
import time


def obtain_orders(user, days=7):
    time.sleep(3)
    try:
        res = Orders(marketplace=Marketplaces.DE, credentials=user.credentials()).get_orders(
            CreatedAfter=(datetime.utcnow() - timedelta(days=days)).isoformat())
        for order in res.payload['Orders']:
            if Order.objects.raw({'AmazonOrderId': order['AmazonOrderId']}).count() == 0:
                Order(user=user, **order).save()
            else:
                pass
        while(res.next_token):
            time.sleep(3)
            res = Orders(marketplace=Marketplaces.DE, credentials=user.credentials()).get_orders(NextToken=res.next_token)
            for order in res.payload['Orders']:
                if Order.objects.raw({'AmazonOrderId': order['AmazonOrderId']}).count() == 0:
                    Order(user=user, **order).save()
                else:
                    pass
    except SellingApiException as ex:
        print(ex)


def obtain_order_items(order):
    time.sleep(6)
    try:
        res = Orders(marketplace=Marketplaces.DE, credentials=order.user.credentials()).get_order_items(
            order_id=order.AmazonOrderId)
        for item in res.payload['OrderItems']:
            OrderItem(order=order, **item).save()
        while(res.next_token):
            time.sleep(6)
            res = Orders(marketplace=Marketplaces.DE, credentials=order.user.credentials()).get_order_items(
                NextToken=res.next_token)
            for item in res.payload['OrderItems']:
                OrderItem(order=order, **item).save()
        if OrderItem.objects.raw({'order': order._id}).count() > 0:
            order.has_items = True
            order.save()
    except SellingApiException as ex:
        print(ex)
