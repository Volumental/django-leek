from django.conf.urls import url
from test_app.views import *

urlpatterns = [
    url(r'^$', index),
]
