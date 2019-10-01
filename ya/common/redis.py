from django_redis import get_redis_connection


class Redis:
    __instance = None

    @classmethod
    def get_instance(cls):
        if cls.__instance is None:
            cls.__instance = get_redis_connection("default")
        return cls.__instance
