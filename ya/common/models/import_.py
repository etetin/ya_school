import json

from ya.common.exception import ImportNotExist
from django_redis import get_redis_connection


class Import:
    def __init__(self, import_id=None):
        self._redis = get_redis_connection("default")

        if import_id is None:
            self.create()
        elif not self._redis.exists(f'import_id:{import_id}'):
            raise ImportNotExist
        else:
            self.import_id = import_id

    def create(self):
        self.import_id = self._redis.incr('import_id')

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

    def get_data(self, to_dict=False):
        data = self._redis.hgetall(f'import_id:{self.import_id}')

        if to_dict:
            result = {
                int(citizen_id): json.loads(data[citizen_id])
                for citizen_id in data
            }
        else:
            #TODO duplicate with citizen.py line 35
            result = [
                {'citizen_id': citizen_id, **json.loads(data[citizen_id])}
                for citizen_id in data
            ]

        return result
