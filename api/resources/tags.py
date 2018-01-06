from flask_restful import Resource

from ..extensions import restful_api


@restful_api.resource('/tags')
class Tags(Resource):
    pass
