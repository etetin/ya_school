#!/bin/sh

set -e

SERVER_NAME=$(curl ifconfig.me)
echo "from .local import *\nALLOWED_HOSTS = [\n    '$SERVER_NAME',\n]\n\nDATABASES['default']['USER'] = '<ya_user>'\nDATABASES['default']['PASSWORD'] = 'ya_user'" > $PWD/ya/config/__init__.py

sudo cp $PWD/ya/config/nginx.conf /etc/nginx/sites-enabled/ya.nginx.conf

sudo ln -sf $PWD/ya/config/supervisor.conf /etc/supervisor/conf.d/ya.supervisor.conf
sudo supervisorctl reread
sudo supervisorctl update
sudo supervisorctl restart ya_school