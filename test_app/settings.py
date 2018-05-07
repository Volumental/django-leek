import os
ALLOWED_HOSTS = ['localhost', '127.0.0.1']
SECRET_KEY = "not so secret"

DEBUG=True

INSTALLED_APPS = [
    'django_leek'
]

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': 'db.sqlite3',
    }
}

ROOT_URLCONF = 'test_app.app'

PROJECT_PATH = os.path.realpath(os.path.dirname(__file__))
TEMPLATES = [{
    'BACKEND': 'django.template.backends.django.DjangoTemplates',
    'DIRS': [ os.path.join(PROJECT_PATH, 'templates/')]}
]
