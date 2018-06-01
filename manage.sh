#!/bin/sh
APP=$1
shift
. venv/bin/activate
django-admin $@ --pythonpath=. --settings=$APP.settings
