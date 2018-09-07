from django.conf.urls import url
from django.http import HttpResponse
from django.shortcuts import render
from django.db import models

from django_leek.api import Leek, push_task_to_queue

leek = Leek()


class Person(models.Model):
    name = models.CharField(max_length=30)


@leek.task
def hello(to):
    person = Person.objects.create(name="to")
    person.save()

    print('Hello {}!'.format(to))


def index(request):
    if 'queue' in request.GET:
        # Run sync
        hello(to='sync')
        
        # Run async
        hello.offload(to='kwargs')
        hello.offload('args')

        push_task_to_queue(hello, to='old')
        return render(request, 'index.html', {'message': '✓ task queued'})

    return render(request, 'index.html')


urlpatterns = [
    url(r'^$', index),
]
