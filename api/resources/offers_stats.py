from datetime import (
    datetime,
    timedelta,
)
from collections import OrderedDict

import pymongo

from flask import (
    current_app,
    request,
)

from .base import JobsbrowserResource
from ..extensions import restful_api


@restful_api.resource('/offers/stats')
class OffersStats(JobsbrowserResource):
    def get(self):
        return self._get_actual_offers_per_day()

    @staticmethod
    def _parse_date(date_str):
        date_format = current_app.config.get('DATE_FORMAT')
        return datetime.strptime(date_str, date_format).date()

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

    def _get_offers(self, start_date=None, end_date=None, tags=None, **kwargs):
        filter_ = dict()
        if start_date:
            filter_['valid_through'] = {'$gte': str(start_date)}
        if end_date:
            filter_['date_posted'] = {'$lte': str(end_date)}
        if tags:
            filter_['tags'] = {'$all': tags}
        kwargs.setdefault('projection', {})
        kwargs['projection'].update({'_id': False})
        kwargs.setdefault('filter', {})
        kwargs['filter'].update(filter_)
        return self.collections.offers.find(**kwargs)

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

    def _daterange(self, start_date, end_date, days_step=1):
        current_date = start_date
        days = timedelta(days=days_step)
        while current_date <= end_date:
            yield current_date
            current_date += days

    def _parse_args(self):
        args = dict()
        if request.args.get('from'):
            args['from'] = self._parse_date(request.args['from'])
        else:
            oldest_date = self._get_offers(
                projection={'date_posted': True},
                sort=[('date_posted', pymongo.ASCENDING)],
                limit=1,
            ).next()['date_posted']
            args['from'] = self._parse_date(oldest_date)

        if request.args.get('to'):
            args['to'] = self._parse_date(request.args['to'])
        else:
            args['to'] = datetime.today().date()

        args['tags'] = list()
        for tags in request.args.getlist('tags'):
            args['tags'].extend(tags.split(','))
        return args
