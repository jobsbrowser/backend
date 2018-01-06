from datetime import (
    date,
    timedelta,
)

from flask import current_app
from flask_restful import Resource

from ..extensions import (
    mongo,
    restful_api,
)


@restful_api.resource('/info')
class Info(Resource):
    def get(self):
        response = dict()
        offers_collection = mongo.db[current_app.config.get(
            'OFFERS_COLLECTION',
        )]
        response['offers_number'] = offers_collection.count()
        response['last_crawl_date'] = str(date.today())
        response.update(self._get_offers_number_per_date())
        return response

    def _get_offers_number_per_date(self):
        days = list()
        offer_count = list()
        days_window = current_app.config.get('DAYS_WINDOW')
        day_delta = timedelta(days=1)
        current_day = date.today() - timedelta(days=days_window - 1)
        offers_collection = mongo.db[current_app.config.get(
            'OFFERS_COLLECTION',
        )]
        for _ in range(days_window):
            days.append(str(current_day))
            offer_count.append(offers_collection.count(
                    filter={'date_posted': {'$lte': str(current_day)}},
            ))
            current_day += day_delta
        return {'days': days, 'offers_count': offer_count}
