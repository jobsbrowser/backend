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
