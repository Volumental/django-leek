import datetime
import pickle
import base64

from . import models
from .task import Task


def unpack(pickled_task):
    new_task = pickle.loads(base64.b64decode(pickled_task))
    assert isinstance(new_task, Task)
    return new_task


def serielize(task):
    return base64.b64encode(pickle.dumps(task))


def load_task(task_id):
    return models.QueuedTasks.objects.get(pk=task_id)


def save_task_to_db(new_task):
    pickled_task = serielize(new_task)
    t = models.QueuedTasks(pickled_task=pickled_task)
    t.save()
    return t
