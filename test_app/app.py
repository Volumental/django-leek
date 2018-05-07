from django.conf.urls import url
from django.http import HttpResponse
from django.shortcuts import render

from django_leek.API import push_task_to_queue

def task():
    print('Executed on queue!')


def index(request):
    if 'queue' in request.GET:
        push_task_to_queue(task)
        return render(request, 'index.html', {'message': '✓ task queued'})

    return render(request, 'index.html')


urlpatterns = [
    url(r'^$', index),
]
