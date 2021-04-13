# coding: utf-8

from flask import Flask
from config import environment_mapping
from flask_wtf import CSRFProtect
import logging
from logging.handlers import RotatingFileHandler
from main.utils.commons import ReConverter
from flask_apscheduler import APScheduler
from apscheduler.schedulers.background import BackgroundScheduler
from flask_httpauth import HTTPTokenAuth
import os
import asyncio


auth = HTTPTokenAuth(scheme='Token')

scheduler = APScheduler(BackgroundScheduler(timezone="Asia/Shanghai"))

# 设置日志的记录等级
logging.basicConfig(level=logging.DEBUG)  # 调试debug级
# 创建日志记录器，指明日志保存的路径、每个日志文件的最大大小、保存的日志文件个数上限
file_log_handler = RotatingFileHandler("logs/log", maxBytes=1024*1024*10, backupCount=100)
# 创建日志记录的格式               日志等级     文件名        行数        日志信息
formatter = logging.Formatter('%(asctime)s %(levelname)s %(filename)s:%(lineno)d %(message)s', "%Y%m%d-%H:%M:%S")
# 为日志记录器设置格式
file_log_handler.setFormatter(formatter)
# 为全局日志工具对象添加日志记录器
logging.getLogger().addHandler(file_log_handler)


def orders_query():
    """订单数据获取定时任务"""
    with app.app_context():
        if os.path.exists('shutdown.txt'):
            return
        from main.utils.orders import obtain_orders

        async def process_order(user):
            try:
                obtain_orders(user, days=20)
                return "process_order success"
            except Exception as error:
                return "process_order error-{}".format(error)

        new_loop = asyncio.new_event_loop()
        asyncio.set_event_loop(new_loop)
        loop = asyncio.get_event_loop()
        try:
            from main.models import User
            tasks = [asyncio.ensure_future(process_order(user)) for user in User.objects.all()]
            print(len(tasks))

            loop.run_until_complete(asyncio.wait(tasks))

            for task in tasks:
                print('Task orders_query ret: ', task.result())
        except Exception as e:
            print("orders_query error-{}".format(e))


def order_items_query():
    pass


# 工厂方法
def create_app(environment):
    """
    创建flask的应用对象
    #param environment: string 配置环境名称 ("development", "production")
    #return:
    """
    app = Flask(__name__)
    app.config.from_object(environment_mapping.get(environment))

    # 定时任务相关配置
    app.config.update(
        {
            'JOBS': [
                {
                    'id': 'orders_query',
                    'func': orders_query,
                    "trigger": "interval",
                    "days": 1
                }
            ],
            'SCHEDULER_TIMEZONE': 'Asia/Shanghai',
            'SCHEDULER_API_ENABLED': True,
            'SCHEDULER_JOB_DEFAULTS': {'max_instances': 3}
        }
    )

    scheduler.init_app(app)

    # csrf保护
    # CSRFProtect(app)

    # 为flask添加自定义的转换器
    app.url_map.converters["re"] = ReConverter

    # 注册蓝图
    from main.api_1_0 import api as api_blueprint
    app.register_blueprint(api_blueprint, url_prefix="/api/v1.0")

    # 注册提供静态文件的蓝图
    from main import web_html
    app.register_blueprint(web_html.html)

    return app


app = create_app("development")
