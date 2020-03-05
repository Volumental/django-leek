import socket
from functools import wraps
import json

from . import models
from . import helpers
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


def push_task_to_queue(a_callable, *args, **kwargs):
    """Original API"""
    pool_name = kwargs.pop('pool_name', None)
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)    
    new_task = Task(a_callable, *args, **kwargs)
    queued_task = helpers.save_task_to_db(new_task, pool_name)
    sock.connect((HOST, PORT))
    sock.send("{}".format(queued_task.id).encode())
    received = sock.recv(1024)
    sock.close()
    return json.loads(received.decode())


def query_task(task_id: int) -> models.Task:
    return helpers.load_task(task_id)
