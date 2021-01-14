#! /bin/bash

directory="/opt/comer_web/"

cd $directory/src

echo 'Creating virtual environment.'
python3 -m venv virtualenv

echo 'Activating virtual environment.'
source virtualenv/bin/activate

echo 'Installing dependencies.'
pip install -r requirements.txt

echo 'Getting comer-ws-backend settings.'
python scripts/get_comer_ws_backend_settings.py > comer_web/settings/comer_ws_backend.py

echo 'Setting up Django.'
python manage.py makemigrations
python manage.py migrate
python manage.py collectstatic

echo 'Deactivating virtual environment.'
deactivate

