import datetime
import pickle
import base64
from functools import partial

from . import models


def unpack(pickled_task):
    new_task = pickle.loads(base64.b64decode(pickled_task))
    assert isinstance(new_task, partial)
    return new_task


def serialize(task):
    return base64.b64encode(pickle.dumps(task))


def load_task(task_id):
    return models.QueuedTasks.objects.get(pk=task_id)


def save_task_to_db(new_task, pool_name):
    pickled_task = serialize(new_task)
    t = models.QueuedTasks(pickled_task=pickled_task, pool=pool_name)
    t.save()
    return t
