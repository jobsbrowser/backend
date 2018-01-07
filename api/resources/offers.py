from flask import (
    current_app,
    request,
)

from .base import JobsbrowserResource
from ..extensions import restful_api


@restful_api.resource('/offers')
class Offers(JobsbrowserResource):
    def get(self):
        return self._paginate(self.collections.offers.find(
            filter={'tags': {'$all': self.args['tags']}},
            projection={'_id': False},
        ))

    def _parse_args(self):
        args = dict()
        args['page_number'] = int(request.args.get('page_number', 1))
        args['page_size'] = int(request.args.get(
            'page_size',
            current_app.config.get('DEFAULT_PAGE_SIZE'),
        ))
        args['tags'] = list()
        for tags in request.args.getlist('tags'):
            args['tags'].extend(tags.split(','))
        return args

    def _paginate(self, cursor):
        offers_number = cursor.count()
        has_more = ((self.args['page_number'] + 1) * self.args['page_size'] <
                    offers_number)
        pages_to_skip = self.args['page_size'] * (self.args['page_number'] - 1)
        offers = list(cursor.skip(pages_to_skip).limit(self.args['page_size']))
        return {'has_more': has_more, 'offers': offers}
