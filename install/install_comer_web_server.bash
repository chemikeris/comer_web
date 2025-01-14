#! /bin/bash

set -o errexit

directory="/opt/comer_web/"

cd $directory/src

echo 'Creating virtual environment.'
python3.12 -m venv virtualenv

echo 'Activating virtual environment.'
source virtualenv/bin/activate

echo 'Installing dependencies.'
pip install --upgrade pip
pip install -r requirements.txt

echo 'Creating necessary Django configuration.'
echo "DEBUG = False" > comer_web/settings/debug.py


echo 'Setting up Django.'
python manage.py makemigrations
python manage.py makemigrations databases
python manage.py makemigrations core
python manage.py makemigrations search
python manage.py makemigrations model_structure
python manage.py makemigrations msa
python manage.py makemigrations website
python manage.py makemigrations structure_search
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
su comerws sh -c 'python manage.py create_example_gtalign_job'

echo 'Deactivating virtual environment.'
deactivate

echo 'Reloading httpd.'
service httpd reload
