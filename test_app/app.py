import time
import json

from django.conf.urls import url
from django.forms.models import model_to_dict
from django.core.serializers.json import DjangoJSONEncoder
from django.http import HttpResponse
from django.shortcuts import render
from django.db import models

from django_leek.api import Leek, push_task_to_queue, query_task

leek = Leek()


class Person(models.Model):
    name = models.CharField(max_length=30)


@leek.task
def hello(to):
    raise ValueError('ops')
    #person = Person.objects.create(name="to")
    #person.save()

    #print('Hello {}!'.format(to))
    #return 'ok'


@leek.task
def slow(seconds: int):
    person = Person.objects.create(name="to")
    person.save()
    print('sleeping')
    time.sleep(seconds)
    print('ok')
    return 'ok'


def index(request):
    if 'queue' in request.GET:
        # Run sync
        #hello(to='sync')
        
        # Run async
        r = hello.offload(to='kwargs')
        #r = slow.offload(seconds=5)

        push_task_to_queue(hello, to='old')
        return render(request, 'index.html', {
            'message': '✓ task queued',
            'task_id': r['task_id']
        })

    return render(request, 'index.html', {'task_id': None})


def query(request, task_id):
    task = query_task(task_id)
    data = {
        'queued_on': task.queued_on,
        'started_at': task.started_at,
        'finished_at': task.finished_at,
        'exception': str(task.exception),
        'return_value': task.return_value
    }
    return HttpResponse(
        json.dumps(data, cls=DjangoJSONEncoder),
        content_type='application/json')


urlpatterns = [
    url(r'^$', index),
    url(r'^query/(\d+)/?$', query)
]
