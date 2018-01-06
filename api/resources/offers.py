from .base import JobsbrowserResource
from ..extensions import restful_api


@restful_api.resource('/offers')
class Offers(JobsbrowserResource):
    pass
