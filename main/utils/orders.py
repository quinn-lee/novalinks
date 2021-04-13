# coding:utf-8

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
                Order.objects.raw({'AmazonOrderId': order['AmazonOrderId']}).update({'$set': order})
                order1 = Order.objects.raw({'AmazonOrderId': order['AmazonOrderId']}).first()
                if order.get('EarliestDeliveryDate') is not None:
                    order1.EarliestDeliveryDate = order.get('EarliestDeliveryDate')
                if order.get('EarliestShipDate') is not None:
                    order1.EarliestShipDate = order.get('EarliestShipDate')
                if order.get('LastUpdateDate') is not None:
                    order1.LastUpdateDate = order.get('LastUpdateDate')
                if order.get('LatestDeliveryDate') is not None:
                    order1.LatestDeliveryDate = order.get('LatestDeliveryDate')
                if order.get('LatestShipDate') is not None:
                    order1.LatestShipDate = order.get('LatestShipDate')
                if order.get('PurchaseDate') is not None:
                    order1.PurchaseDate = order.get('PurchaseDate')
                if order.get('PromiseResponseDueDate') is not None:
                    order1.PromiseResponseDueDate = order.get('PromiseResponseDueDate')
                order1.has_items = False
                order1.save()
        while(res.next_token):
            time.sleep(3)
            res = Orders(marketplace=Marketplaces.DE, credentials=user.credentials()).get_orders(NextToken=res.next_token)
            for order in res.payload['Orders']:
                if Order.objects.raw({'AmazonOrderId': order['AmazonOrderId']}).count() == 0:
                    Order(user=user, **order).save()
                else:
                    Order.objects.raw({'AmazonOrderId': order['AmazonOrderId']}).update({'$set': order})
                    order1 = Order.objects.raw({'AmazonOrderId': order['AmazonOrderId']}).first()
                    if order.get('EarliestDeliveryDate') is not None:
                        order1.EarliestDeliveryDate = order.get('EarliestDeliveryDate')
                    if order.get('EarliestShipDate') is not None:
                        order1.EarliestShipDate = order.get('EarliestShipDate')
                    if order.get('LastUpdateDate') is not None:
                        order1.LastUpdateDate = order.get('LastUpdateDate')
                    if order.get('LatestDeliveryDate') is not None:
                        order1.LatestDeliveryDate = order.get('LatestDeliveryDate')
                    if order.get('LatestShipDate') is not None:
                        order1.LatestShipDate = order.get('LatestShipDate')
                    if order.get('PurchaseDate') is not None:
                        order1.PurchaseDate = order.get('PurchaseDate')
                    if order.get('PromiseResponseDueDate') is not None:
                        order1.PromiseResponseDueDate = order.get('PromiseResponseDueDate')
                    order1.has_items = False
                    order1.save()
    except SellingApiException as ex:
        print(ex)


def obtain_order_items(order):
    time.sleep(6)
    try:
        res = Orders(marketplace=Marketplaces.DE, credentials=order.user.credentials()).get_order_items(
            order_id=order.AmazonOrderId)
        for item in res.payload['OrderItems']:
            if OrderItem.objects.raw({'OrderItemId': order['OrderItemId'], 'order': order._id}).count() == 0:
                OrderItem(order=order, **item).save()
            else:
                OrderItem.objects.raw({'OrderItemId': order['OrderItemId'], 'order': order._id}).update({'$set': item})
                order_item = OrderItem.objects.raw({'OrderItemId': order['OrderItemId'], 'order': order._id}).first()
                if item.get('ScheduledDeliveryStartDate') is not None:
                    order_item.ScheduledDeliveryStartDate = item.get('ScheduledDeliveryStartDate')
                if item.get('ScheduledDeliveryEndDate') is not None:
                    order_item.ScheduledDeliveryEndDate = item.get('ScheduledDeliveryEndDate')
                order_item.save()
        while(res.next_token):
            time.sleep(6)
            res = Orders(marketplace=Marketplaces.DE, credentials=order.user.credentials()).get_order_items(
                NextToken=res.next_token)
            for item in res.payload['OrderItems']:
                if OrderItem.objects.raw({'OrderItemId': order['OrderItemId'], 'order': order._id}).count() == 0:
                    OrderItem(order=order, **item).save()
                else:
                    OrderItem.objects.raw({'OrderItemId': order['OrderItemId'], 'order': order._id}).update(
                        {'$set': item})
                    order_item = OrderItem.objects.raw(
                        {'OrderItemId': order['OrderItemId'], 'order': order._id}).first()
                    if item.get('ScheduledDeliveryStartDate') is not None:
                        order_item.ScheduledDeliveryStartDate = item.get('ScheduledDeliveryStartDate')
                    if item.get('ScheduledDeliveryEndDate') is not None:
                        order_item.ScheduledDeliveryEndDate = item.get('ScheduledDeliveryEndDate')
                    order_item.save()
        if OrderItem.objects.raw({'order': order._id}).count() > 0:
            order.has_items = True
            order.save()
    except SellingApiException as ex:
        print(ex)


def obtain_order_address(order):
    time.sleep(6)
    try:
        res = Orders(marketplace=Marketplaces.DE, credentials=order.user.credentials()).get_order_address(
            order_id=order.AmazonOrderId)
        if res.payload.get('ShippingAddress') is not None:
            order.ShippingAddress = res.payload.get('ShippingAddress')
            order.save()
    except SellingApiException as ex:
        print(ex)