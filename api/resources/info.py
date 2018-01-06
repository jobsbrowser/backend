from datetime import (
    date,
    timedelta,
)

from flask import current_app

from .base import JobsbrowserResource
from ..extensions import restful_api


@restful_api.resource('/info')
class Info(JobsbrowserResource):
    def get(self):
        response = dict()
        response['offers_number'] = self.collections.offers.count()
        response['last_crawl_date'] = str(date.today())
        response.update(self._get_offers_number_per_date())
        return response

    def _get_offers_number_per_date(self):
        days = list()
        offer_count = list()
        days_window = current_app.config.get('DAYS_WINDOW')
        day_delta = timedelta(days=1)
        current_day = date.today() - timedelta(days=days_window - 1)
        for _ in range(days_window):
            days.append(str(current_day))
            offer_count.append(self.collections.offers.count(
                    filter={'date_posted': {'$lte': str(current_day)}},
            ))
            current_day += day_delta
        return {'days': days, 'offers_count': offer_count}
