import socket
from functools import wraps, partial
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


def push_task_to_queue(a_callable, pool_name=None, *args, **kwargs):
    """Original API"""
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)    
    new_task = partial(a_callable, *args, **kwargs)
    queued_task = helpers.save_task_to_db(new_task, pool_name)
    sock.connect((HOST, PORT))
    sock.send("{}".format(queued_task.id).encode())
    received = sock.recv(1024)
    sock.close()

    return received
