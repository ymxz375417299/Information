# coding=utf-8
# 配置模块

import redis
import logging


class Config:
    """工程配置信息"""
    DEBUG = True
    # # 默认host和端口
    # HOST = '0.0.0.0'
    # PORT = 5000
    # mysql配置
    SQLALCHEMY_DATABASE_URI = 'mysql://root:mysql@127.0.0.1:3306/information'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    # redis配置
    REDIS_HOST = '127.0.0.1'
    REDIS_PORT = 6379
    # 安全秘钥
    SECRET_KEY = 'RFIAGD3GEemj+qx7oUa2IERSABk9xhHpnmGse6FGtiA='
    SESSION_TYPE = 'redis' # session保存到redis
    SESSION_REDIS = redis.StrictRedis(host=REDIS_HOST, port=REDIS_PORT) # 使用自己导入的redis的实例，默认会自己帮我们传，但是会把端口配置固定，不够灵活
    SESSION_USE_SIGNER = True # 让cookie中的session_id 被加密签名处理
    SESSION_PERMANENT = False # 设置session过期
    PERMANENT_SESSION_LIFETIME = 86400 * 2 # session的有效期2天，单位秒，默认31天


class DevelopmentConfig(Config):
    """开发模式的配置"""
    DEBUG = True
    LOG_EVEL = logging.DEBUG

class ProductionConfig(Config):
    """生产模式的配置"""
    DEBUG = False
    LOG_EVEL = logging.ERROR

class TestingConfig(Config):
    """单元测试的环境的配置"""
    DEBUG = True
    TESTING = True
    LOG_EVEL = logging.DEBUG

config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
}
