import socket
from functools import wraps
from .task import Task
from . import helpers
from .settings import HOST, PORT


class Leek(object):
    def task(self, f):
        @wraps(f)
        def _offload(*args, **kwargs):
            return push_task_to_queue(f, *args, **kwargs)
        f.offload = _offload
        return f


def push_task_to_queue(a_callable, *args, **kwargs):
    """Original API"""
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)    
    new_task = Task(a_callable, *args, **kwargs)
    queued_task = helpers.save_task_to_db(new_task)
    sock.connect((HOST, PORT))
    sock.send("{}".format(queued_task.id).encode())
    received = sock.recv(1024)
    sock.close()

    return received
