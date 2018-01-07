from flask import (
    current_app,
    request,
)

from .base import BaseOffersResource
from ..extensions import restful_api


@restful_api.resource('/offers')
class Offers(BaseOffersResource):
    def get(self):
        return self._paginate(self._get_offers(
            tags=self.args['tags'],
            filter={
                'valid_through': {'$gte': str(self.args['from'])},
                'date_posted': {'$lte': str(self.args['to'])},
            }
        ))

    def _parse_args(self):
        args = super()._parse_args()
        args['page_number'] = int(request.args.get('page_number', 1))
        args['page_size'] = int(request.args.get(
            'page_size',
            current_app.config.get('DEFAULT_PAGE_SIZE'),
        ))
        return args

    def _paginate(self, cursor):
        offers_number = cursor.count()
        has_more = ((self.args['page_number'] + 1) * self.args['page_size'] <
                    offers_number)
        pages_to_skip = self.args['page_size'] * (self.args['page_number'] - 1)
        offers = list(cursor.skip(pages_to_skip).limit(self.args['page_size']))
        return {'has_more': has_more, 'offers': offers}
