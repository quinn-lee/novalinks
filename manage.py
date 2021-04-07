# coding:utf-8


from flask_script import Manager
from main import app, scheduler
from flask_script import Shell
from main.models import User, UserLog, Order, OrderItem, Inventory
from getpass import getpass
from werkzeug.security import generate_password_hash
from main.utils.orders import obtain_orders, obtain_order_items
from main.utils.inventories import obtain_inventories, obtain_catalogs


# 初始化管理器
manager = Manager(app)


def make_shell_context():
    return dict(app=app, User=User, UserLog=UserLog, Order=Order, OrderItem=OrderItem, Inventory=Inventory,
                scheduler=scheduler, obtain_orders=obtain_orders, obtain_order_items=obtain_order_items)


manager.add_command('shell', Shell(make_context=make_shell_context))


@manager.command
def adduser():
    name = input('Username> ')
    email = input('Email> ')
    input_password = getpass('Password> ')
    new = User(name=name, email=email, pwd=generate_password_hash(input_password))
    new.save()
    print("new user <%s> created" % name)


@manager.command
def process_orders():
    days = int(input('Days> '))
    for user in User.objects.all():
        obtain_orders(user, days=days)


@manager.command
def process_order_items():
    i = 0
    for order in Order.objects.raw({'has_items': False}).all():
        obtain_order_items(order)
        if i > 50:  # 时间太长时会报CursorNotFound
            break
        i += 1


@manager.command
def process_inventories():
    for user in User.objects.all():
        obtain_inventories(user)


@manager.command
def process_catalogs():
    i = 0
    for inventory in Inventory.objects.raw({'has_attrs': False}).all():
        obtain_catalogs(inventory)
        if i > 50:  # 时间太长时会报CursorNotFound
            break
        i += 1


if __name__ == "__main__":
    manager.run()
