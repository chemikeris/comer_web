#! /bin/bash

set -o errexit

directory="/opt/comer_web/"

cd $directory/src
source virtualenv/bin/activate

secret_key=$(python -c "from django.core.management.utils import get_random_secret_key as _; sc=_(); print(sc)")

passwords_file="comer_web/settings/passwords.py"
if [ -f $passwords_file ]; then
    echo 'Passwords file found.'
    if grep "^SECRET_KEY" $passwords_file > /dev/null; then
        true
    else
        echo "SECRET_KEY = '$secret_key'" >> $passwords_file
    fi
else
    echo 'Generating passwords.py'
    echo "$secret_key" > $passwords_file
fi

deactivate
