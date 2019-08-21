# YA school

Project for admission to yandex backend-school.

## Notice

For requests `POST /imports` and `PATCH imports/<int:import_id>/citizens/<int:citizen_id>` need to set header `Content-Type: application/json`


## Getting Started

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes. See deployment for notes on how to deploy the project on a live system.

### Prerequisites

Install required system packages.

```
$ sudo apt-get update
$ sudo apt-get install git nginx supervisor python3.7 python3.7-venv python3.7-dev build-essential python3-pip postgresql postgresql-contrib 
```

#### Add a new user to system

> If you want to change your username, don't forget to also change username in the configs of ya/config/gunicorn.conf.py and ya/config/supervisor.conf 


```
$ adduser entrant
```

Set and confirm the new user's password at the prompt. 
```
Set password prompts:
Enter new UNIX password:
Retype new UNIX password:
passwd: password updated successfully
```

Set the new user's information.
```
User information prompts:
Changing the user information for username
Enter the new value, or press ENTER for the default
    Full Name []:
    Room Number []:
    Work Phone []:
    Home Phone []:
    Other []:
Is the information correct? [Y/n]
```

Add the user to the sudo group.
```
$ usermod -aG sudo entrant
```

Authorize by the created user
```
$ su entrant
```

Test sudo access on new user
```
$ sudo ls -la /root
$ cd ~
```


#### Set up postgres
Create user and database
```
$ sudo -u postgres createuser ya_user
$ sudo -u postgres createdb ya_api
```
> If you want to change database name, don't forget to also change it in ya/config/common.py

Giving the user a password and granting privileges on database
```
$ sudo -u postgres psql
postgres=# alter user ya_user with encrypted password 'ya_user';
postgres=# alter user ya_user CREATEDB;
postgres=# grant all privileges on database ya_api to ya_user;
```
> If you want to change username and password, don't forget to also change username and password in ya/config/\__init__.py, after you run the web.sh

### Installing

Create base directory for project and venv and go to it
```
$ mkdir "ya_school" && cd $_;
```

Create venv
```
$ python3.7 -m venv env
```

Activate venv and clone repository
```
$ source env/bin/activate
(env) $ git clone https://github.com/etetin/ya_school.git
```

Move into project directory

```
(env) $ cd ya_school
```

Install requirements
```
(env) $ pip install -r requirements.txt
```

Run script for choosing django config and creating links for supervisor and create copy nginx.conf  
```
(env) $ sh web.sh
```

In /etc/nginx/sites-enabled/ya.nginx.conf replace <server_ip> on actual server ip and after this restart nginx
```
(env) $ sudo nano /etc/nginx/sites-enabled/ya.nginx.conf
(env) $ sudo service nginx restart
```  

Apply migrations
```
(env) $ python manage.py migrate
```

Check statuses of nginx and supervisor
```
(env) $ sudo service nginx status
(env) $ sudo supervisorctl status ya_school
```
If nginx is running and the answer supervisor looks like lines below, the project was successfully launched. 
```
ya_school                        RUNNING   pid 12920, uptime 0:00:31
```


## Running the tests

```
(env) $ python manage.py test ya.api 
```

## Deployment

If nginx conf has been changed, need to create his copy. Replace server_name if it need and restart nginx.
```
sudo cp $PWD/ya/config/nginx.conf /etc/nginx/sites-enabled/ya.nginx.conf
sudo service nginx restart
```

Apply new migrations.
```
(env) $ python manage.py migrate
```

For restarting service enter command.
```
$ sudo supervisorctl restart ya_school
```

