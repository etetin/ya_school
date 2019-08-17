#!/bin/sh

set -e

echo "from .prod import *" >> $PWD/ya/config/__init__.py

sudo ln -sf $PWD/ya/config/nginx.conf /etc/nginx/sites-enabled/ya.nginx.conf
sudo service nginx restart

sudo ln -sf $PWD/ya/config/supervisor.conf /etc/supervisor/conf.d/ya.supervisor.conf
sudo supervisorctl reread
sudo supervisorctl update
sudo supervisorctl restart ya_school