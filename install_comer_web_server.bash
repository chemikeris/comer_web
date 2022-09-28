#! /bin/bash

set -o errexit

directory="/opt/comer_web/"

cd $directory/src

echo 'Creating virtual environment.'
python3 -m venv virtualenv

echo 'Activating virtual environment.'
source virtualenv/bin/activate

echo 'Installing dependencies.'
pip install --upgrade pip
pip install -r requirements.txt

echo 'Creating necessary Django configuration.'
echo "DEBUG = False" > comer_web/settings/debug.py
passwords_file="comer_web/settings/passwords.py"
if [ -f $passwords_file ]; then
    echo 'Passwords file found.'
else
    echo 'Generating passwords.py'
    python -c "from django.core.management.utils import get_random_secret_key as _; sc=_(); print(f\"SECRET_KEY = '{sc}'\")" > $passwords_file
fi

echo 'Setting up Django.'
python manage.py makemigrations
python manage.py makemigrations core
python manage.py makemigrations search
python manage.py makemigrations model_structure
python manage.py makemigrations msa
python manage.py makemigrations website
python manage.py migrate
python manage.py collectstatic --noinput

echo 'Getting available databases from comer-ws-backend settings.'
su comerws sh -c 'python manage.py get_comer_ws_backend_databases'

echo 'Setting ownership for files and directories.'
chown -R comerws:comerws $directory

echo 'Copying configuration files.'
cp comer.conf /etc/httpd/conf.d/

echo 'Installing and running COMER server daemon.'
cp comer.service /etc/systemd/system/
systemctl daemon-reload
systemctl enable --now comer.service
service comer restart

echo 'Creating example job, if necessary.'
su comerws sh -c 'python manage.py create_example_job'

echo 'Deactivating virtual environment.'
deactivate

echo 'Reloading httpd.'
service httpd reload
