#!/bin/sh
set -ex

flake8 .

rm -f .coverage
coverage run manage.py test --noinput --settings=service_info.settings.dev "$@"
coverage report
