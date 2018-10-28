# -*- coding: utf-8 -*-
import os
import logging


class Config(object):
    """Common config parameters."""
    # The secret key is used by Flask to encrypt session cookies.
    SECRET_KEY = 'EwJp9uQQzEHt2LfWagJL8pve'

    # Flask reload
    TEMPLATES_AUTO_RELOAD = True

    # Site root
    SITE_ROOT = os.path.realpath(os.path.dirname(__file__))

    # Set the position of the pricing file
    PRICING_JSON_URI = os.path.join(SITE_ROOT, u'pricing.json')


class DevelopmentConfig(Config):
    # Set the logging level
    LOGGING_LEVEL = logging.DEBUG


class TestConfig(Config):
    # Set the logging level
    LOGGING_LEVEL = logging.DEBUG


class StageConfig(Config):
    # Set the logging level
    LOGGING_LEVEL = logging.WARNING


class ProductionConfig(Config):
    # Set the logging level
    LOGGING_LEVEL = logging.ERROR


app_config = {
    u'devel': DevelopmentConfig,
    u'test': TestConfig,
    u'staging': StageConfig,
    u'production': ProductionConfig,
}
