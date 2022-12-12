import json
import socket
import sys
from functools import wraps
from typing import Iterator, Optional, Tuple

from . import helpers
from . import models
from .settings import HOST, PORT


class Leek(object):
    def task(self, f, pool=None):
        pool_name = pool or f.__name__

        @wraps(f)
        def _offload(*args, **kwargs):
            return push_task_to_queue(f, pool_name=pool_name, *args, **kwargs)

        f.offload = _offload
        return f


class Task(object):
    def __init__(self, a_callable, *args, **kwargs):
        assert callable(a_callable)
        self.task_callable = a_callable
        self.args = args
        self.kwargs = kwargs

    def __call__(self):
        return self.task_callable(*self.args, **self.kwargs)


def start_task_with_id(task_id: int):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((HOST, PORT))
    sock.send("{}".format(task_id).encode())
    received = sock.recv(1024)
    sock.close()
    return json.loads(received.decode())


def push_task_to_queue(a_callable, *args, **kwargs):
    """Original API"""
    pool_name = kwargs.pop('pool_name', None)

    new_task = Task(a_callable, *args, **kwargs)
    queued_task = helpers.save_task_to_db(new_task, pool_name)

    return start_task_with_id(queued_task.id)


def query_task(task_id: int) -> models.Task:
    return helpers.load_task(task_id)


def list_tasks(finished: Optional[bool] = None) -> Iterator[Tuple[models.Task, Task]]:
    db_tasks = models.Task.objects.all().order_by('queued_at')
    if finished is not None:
        db_tasks = db_tasks.filter(finished_at__isnull=not finished)
    for db_task in db_tasks:
        try:
            task = helpers.unpack(db_task.pickled_task)
            yield db_task, task
        except (ModuleNotFoundError, AttributeError):  # things that can happen during unpickle
            print("could not unpickle task", db_task.id, file=sys.stderr)
