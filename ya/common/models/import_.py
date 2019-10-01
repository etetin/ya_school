from ya.common.exception import ImportNotExist
from ya.common.redis import Redis
# from ..redis import Redis
from .citizen import Citizen


class Import:
    __redis = Redis.get_instance()

    def __init__(self, import_id=None):
        self.import_id = import_id

    def create(self):
        self.import_id = self.__redis.incr('import_id')
        return self.import_id

    def set_citizens(self, citizens_data):
        citizens_data = Citizen.convert_for_insert(data=citizens_data)
        self.__redis.hmset(f'import_id:{self.import_id}', citizens_data)

    def get_data(self):
        data = self.__redis.hgetall(f'import_id:{self.import_id}')
        if data == {}:
            raise ImportNotExist

        return Citizen.convert_to_object(data=data)
