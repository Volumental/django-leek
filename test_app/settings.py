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

ROOT_URLCONF = 'test_app.urls'
