import os


class BaseConfig:
    DEBUG = False
    DEFAULT_PAGE_SIZE = 30
    OFFERS_COLLECTION = 'offers'
    TAGS_COLLECTION = 'tags'
    DAYS_WINDOW = 30
    DATE_FORMAT = '%Y-%m-%d'
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
    return CONFIG_MAPPING.get(config_name.upper(), DevConfig)
