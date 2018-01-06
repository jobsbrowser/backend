import os


class BaseConfig:
    DEBUG = False
    DEFAULT_PAGE_SIZE = 50
    OFFERS_COLLECTION = 'offers'
    TAGS_COLLECTION = 'tags'
    # MONGO_URI = 'mongodb://user:password@url:port/db_name'


class DevConfig(BaseConfig):
    DEBUG = True


class ProductionConfig(BaseConfig):
    pass


class TestingConfig(BaseConfig):
    TESTING = True


CONFIG_MAPPING = {
    'DEV': DevConfig,
    'PRODUCTION': ProductionConfig,
    'TESTING': TestingConfig,
}


def get_config(config_name=None):
    config_name = config_name or os.environ.get('APP_CONFIG') or ""
