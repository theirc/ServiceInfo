#!/bin/sh
set -ex

flake8 .

rm -f .coverage
coverage run manage.py test --noinput --settings=service_info.settings.dev "$@"
coverage report
python manage.py makemigrations --dry-run | grep 'No changes detected' || (echo 'There are changes which require migrations.' && exit 1)
