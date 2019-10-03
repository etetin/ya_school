import json

from ya.common.exception import ImportNotExist
from ya.common.redis import Redis


class Import:
    def __init__(self, import_id=None):
        self._redis = Redis.get_instance()

        if import_id is None:
            self.create()
        elif not self._redis.exists(f'import_id:{import_id}'):
            raise ImportNotExist

        self.import_id = import_id

    def create(self):
        self.import_id = self._redis.incr('import_id')
        return self.import_id

    def set_citizens(self, citizens_data):
        from .citizen import Citizen

        citizens_data = {
            citizen_data['citizen_id']: json.dumps({
                field: citizen_data[field]
                for field in Citizen.FIELDS
            })
            for citizen_data in citizens_data
        }
        self._redis.hmset(f'import_id:{self.import_id}', citizens_data)

    def get_data(self):
        data = self._redis.hgetall(f'import_id:{self.import_id}')

        #TODO duplicate with citizen.py line 35
        return [
            {'citizen_id': citizen_id, **json.loads(data[citizen_id])}
            for citizen_id in data
        ]
