import os
import logging

from werkzeug.contrib.cache import SimpleCache
from flask import Flask

# local import
from config import app_config


def get_config():
    try:
        config = os.getenv('APP_CONFIG', u'devel')
        return config
    except Exception as e:
        print(e.message)
        os.abort()

# setup the cache. I had to use this kind of cache due to the time limit
cache = SimpleCache()

# get the current configuration from environment variable APP_CONFIG
config = get_config()

app = Flask(__name__, instance_relative_config=True)

# load the config.py file
logging.debug(u'Starting with {} configuration'.format(config))
app.config.from_object(app_config[config])

# Set the logging level if settled in config file otherwise set to WARNING level
logging.basicConfig()
level = app.config.get('LOGGING_LEVEL', logging.WARNING)
logging.getLogger().setLevel(level)

# import all the routes
from routes import startup, index
from webapp.api.v1.routes import mod_api_v1 as api_v1

# register the blueprints
app.register_blueprint(api_v1, url_prefix='/api/v1')
