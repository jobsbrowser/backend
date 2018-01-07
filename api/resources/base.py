from datetime import (
    datetime,
    timedelta,
)

import pymongo

from flask import (
    current_app,
    request,
)
from flask_restful import Resource

from ..extensions import mongo


class _CollectionsFromConfigStorage:
    def __init__(self):
        self._storage = {val: None for key, val in current_app.config.items()
                         if key.endswith('_COLLECTION')}

    def __getattr__(self, name):
        if name in self._storage:
            if self._storage[name] is None:
                self._storage[name] = mongo.db[current_app.config.get(
                    f'{name.upper()}_COLLECTION',
                )]
            return self._storage[name]
        raise AttributeError(f'Collection name ({name}) not in config')


class JobsbrowserResource(Resource):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.collections = _CollectionsFromConfigStorage()
        self._args = None

    @property
    def args(self):
        if self._args is None:
            self._args = self._parse_args()
        return self._args

    def _parse_args(self):
        return dict(request.args)


class BaseOffersResource(JobsbrowserResource):
    @staticmethod
    def _parse_date(date_str):
        date_format = current_app.config.get('DATE_FORMAT')
        return datetime.strptime(date_str, date_format).date()

    def _daterange(self, start_date, end_date, days_step=1):
        current_date = start_date
        days = timedelta(days=days_step)
        while current_date <= end_date:
            yield current_date
            current_date += days

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
