from .common import *

DEBUG = False

ALLOWED_HOSTS = [
    # '*',
    '84.201.153.158',
]

# TODO probably it's not best idea store username and password right here.
DATABASES['default']['USER'] = 'postgres'
DATABASES['default']['PASSWORD'] = 'postgres'
