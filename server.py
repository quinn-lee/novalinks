# coding:utf-8

import sys
from tornado.wsgi import WSGIContainer
from tornado.httpserver import HTTPServer
from tornado.ioloop import IOLoop
from main import app, scheduler
import socket

if len(sys.argv) == 2:
    port = sys.argv[1]
else:
    port = 8080

# 防止多进程部署时，定时任务重复启动
try:
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind(("127.0.0.1", 47200))
except socket.error:
    print("!!!scheduler already started, DO NOTHING")
else:
    #scheduler.start()
    print("scheduler started")

http_server = HTTPServer(WSGIContainer(app))
http_server.listen(port)
IOLoop.instance().start()
