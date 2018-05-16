import sys
from django.conf import settings


if 'test' in sys.argv:
    SECRET_KEY="just to make tests run"
    DATABASES = {'default': {'ENGINE': 'django.db.backends.sqlite3', 'NAME': ':memory:'}}
    INSTALLED_APPS = ['django_leek']


cfg = getattr(settings, "LEEK", {})
        
MAX_RETRIES = cfg.get('max_retries', 3)
HOST = cfg.get('host', "localhost")
PORT = int(cfg.get('port', "8002"))
