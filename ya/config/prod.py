from .common import *

DEBUG = False

HOST_ADDRESS = 'http://127.0.0.1:8000'

ALLOWED_HOSTS = [
    # '*',
    '84.201.153.158',
]

# TODO probably it's not best idea store username and password right here.
DATABASES['default']['USER'] = 'postgres'
DATABASES['default']['PASSWORD'] = 'postgres'