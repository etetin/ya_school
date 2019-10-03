import json

from .import_ import Import
from ya.common.exception import CitizenNotExist, WrongRelativeData


def diff(first, second):
    second = set(second)
    return [item for item in first if item not in second]


class Citizen(Import):
    GENDERS = ['male', 'female']
    FIELDS = [
        'town',
        'street',
        'building',
        'apartment',
        'name',
        'birth_date',
        'gender',
        'relatives'
    ]

    def __init__(self, import_id, citizen_id):
        Import.__init__(self, import_id)
        if not self._redis.hexists(f'import_id:{self.import_id}', citizen_id):
            raise CitizenNotExist

        self.citizen_id = citizen_id

        self.data = json.loads(self._redis.hget(f'import_id:{self.import_id}', self.citizen_id))

    def get_data(self):
        return {'citizen_id': self.citizen_id, **self.data}

    def update(self, data):
        updated_relative_citizens = {}
        for field in Citizen.FIELDS:
            value = data.get(field, None)
            if value is None:
                continue

            if field == 'relatives':
                try:
                    for relative_citizen_id in diff(value, self.data['relatives']):
                        relative_citizen = Citizen(import_id=self.import_id, citizen_id=relative_citizen_id)
                        relative_citizen.data['relatives'].append(self.citizen_id)
                        updated_relative_citizens[relative_citizen_id] = json.dumps(relative_citizen.get_data())

                    for relative_citizen_id in diff(self.data['relatives'], value):
                        relative_citizen = Citizen(import_id=self.import_id, citizen_id=relative_citizen_id)
                        relative_citizen.data['relatives'].remove(self.citizen_id)
                        updated_relative_citizens[relative_citizen_id] = json.dumps(relative_citizen.get_data())
                except ValueError:
                    raise WrongRelativeData

            self.data[field] = value

        if updated_relative_citizens:
            updated_relative_citizens[self.citizen_id] = json.dumps(self.get_data())
            self._redis.hmset(f'import_id:{self.import_id}', updated_relative_citizens)
        else:
            self.save()

        return self.get_data()

    def save(self):
        self._redis.hset(
            f'import_id:{self.import_id}',
            self.citizen_id,
            json.dumps(self.data),
        )
