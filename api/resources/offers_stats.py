from datetime import timedelta
from collections import OrderedDict

from .base import BaseOffersResource
from ..extensions import restful_api


@restful_api.resource('/offers/stats')
class OffersStats(BaseOffersResource):
    def get(self):
        return self._get_actual_offers_per_day()

    def _get_actual_offers_per_day(self):
        offers_count = self._cumsum_offers(self._get_offers(
            start_date=self.args['from'],
            end_date=self.args['to'],
            tags=self.args['tags'],
        ))
        all_offers_count = self._cumsum_offers(self._get_offers(
            start_date=self.args['from'],
            end_date=self.args['to'],
        ))
        return {
            'dates': [str(date) for date in self._daterange(
                self.args['from'],
                self.args['to'],
            )],
            'offer_count': offers_count,
            'offer_percentage': [
                tags_offer/all_offers for tags_offer, all_offers in zip(
                    offers_count,
                    all_offers_count,
                )
            ],
        }

    def _cumsum_offers(self, offers):
        buckets = OrderedDict.fromkeys(
            list(self._daterange(self.args['from'], self.args['to'])),
            value=0,
        )
        one_day = timedelta(days=1)
        for i, offer in enumerate(offers):
            date_posted = self._parse_date(offer['date_posted'])
            valid_through = self._parse_date(offer['valid_through'])
            if date_posted < self.args['from']:
                date_posted = self.args['from']
            buckets[date_posted] += 1
            if valid_through < self.args['to']:
                buckets[valid_through + one_day] -= 1
        return self._cumsum(buckets.values())

    def _cumsum(self, sequence):
        offer_count = list()
        total = 0
        for offers_added in sequence:
            total += offers_added
            offer_count.append(total)
        return offer_count
