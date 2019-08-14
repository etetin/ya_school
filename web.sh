#!/bin/sh

set -e

pip install -r requirements.txt

echo "from .prod import *" > $PWD/ya/config/__init__.py

sudo ln -s $PWD/ya/config/nginx.conf /etc/nginx/sites-enabled/ya.nginx.conf
sudo service nginx restart

sudo ln -s $PWD/ya/config/supervisor.conf /etc/supervisor/conf.d/ya.supervisor.conf
sudo supervisorctl reread
sudo supervisorctl update
sudo supervisorctl restart ya_school