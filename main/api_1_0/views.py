# coding:utf-8
from . import api
from main import models
from flask import current_app, request
import time


@api.route("/")
def index():
    current_app.logger.error("error")
    current_app.logger.warning("warning")
    current_app.logger.info("info")
    current_app.logger.debug("debug")


