from .base import JobsbrowserResource
from ..extensions import restful_api


@restful_api.resource('/tags')
class Tags(JobsbrowserResource):
    pass
