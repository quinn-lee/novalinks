# coding: utf-8
import datetime


class Config(object):
    """配置信息"""

    SECRET_KEY = "e096240bbf710ab5053ce04a971ac9bc710099b21df06fcd9ffb1d6a196"

    SEND_FILE_MAX_AGE_DEFAULT = datetime.timedelta(seconds=1)  # 前端静态页面最大缓存时间


class DevelopmentConfig(Config):
    """开发环境配置信息"""
    DEBUG = True


class ProductionConfig(Config):
    """生产环境配置信息"""
    pass


environment_mapping = {
    "development": DevelopmentConfig,
    "production": ProductionConfig
}

