from flask import current_app
from sp_api.api import Orders
from sp_api.base import SellingApiException, Marketplaces
from datetime import datetime, timedelta
from main.models import Order, OrderItem
import time


def obtain_orders(user, days=7):

    try:
        res = Orders(marketplace=Marketplaces.DE, credentials=user.credentials).get_orders(
            CreatedAfter=(datetime.utcnow() - timedelta(days=days)).isoformat())
        for order in res.payload['Orders']:
            if Order.objects.raw({'AmazonOrderId': order['AmazonOrderId']}).count() == 0:
                Order(user=user, **order).save()
                time.sleep(5)
                obtain_items(order['AmazonOrderId'])
            else:
                pass
        while(res.next_token):
            time.sleep(2)
            res = Orders(marketplace=Marketplaces.DE, credentials=user.credentials).get_orders(NextToken=res.next_token)
            for order in res.payload['Orders']:
                if Order.objects.raw({'AmazonOrderId': order['AmazonOrderId']}).count() == 0:
                    Order(user=user, **order).save()
                    time.sleep(2)
                    obtain_items(order['AmazonOrderId'])
                else:
                    pass
    except SellingApiException as ex:
        print(ex)


def obtain_items(order_id):

    try:
        order = Order.objects.raw({'AmazonOrderId': order_id}).first()
        res = Orders(marketplace=Marketplaces.DE, credentials=order.user.credentials).get_order_items(
            order_id=order_id)
        for item in res.payload['OrderItems']:
            OrderItem(order=order, **item).save()
        while(res.next_token):
            time.sleep(2)
            res = Orders(marketplace=Marketplaces.DE, credentials=order.user.credentials).get_order_items(
                NextToken=res.next_token)
            for item in res.payload['OrderItems']:
                OrderItem(order=order, **item).save()
    except SellingApiException as ex:
        print(ex)
