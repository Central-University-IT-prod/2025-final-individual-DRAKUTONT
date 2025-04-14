#!/bin/sh

python manage.py migrate

gunicorn ads_platform.wsgi:application -b :8080 --timeout 120 --workers 3
