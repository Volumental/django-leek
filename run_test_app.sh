#!/bin/sh
. venv/bin/activate
django-admin migrate --pythonpath=. --settings=test_app.settings
django-admin runserver --pythonpath=. --settings=test_app.settings
