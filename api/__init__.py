import importlib

from flask import Flask

from .settings import get_config
from .extensions import (
    mongo,
    restful_api,
)

__all__ = ['create_app']


def create_app(config_name=None, init_extensions=True):
    # register all resources
    importlib.import_module('api.resources')
    app = Flask(__name__)
    app.config.from_object(get_config(config_name))
    if init_extensions:
        mongo.init_app(app)
        restful_api.init_app(app)
    return app
