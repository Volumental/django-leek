import base64
import pickle

from . import models


def unpack(pickled_task: bytes):
    new_task = pickle.loads(base64.b64decode(pickled_task))
    return new_task


def serialize(obj) -> bytes:
    return base64.b64encode(pickle.dumps(obj))


def serialize_exception(e: Exception) -> bytes:
    try:
        return serialize(e)
    except Exception:
        return serialize(Exception("Failed to serialize exception: %s" % e))


def load_task(task_id: int) -> models.Task:
    return models.Task.objects.get(pk=task_id)


def save_task_to_db(new_task, pool_name: str) -> models.Task:
    pickled_task = serialize(new_task)
    t = models.Task(pickled_task=pickled_task, pool=pool_name)
    t.save()
    return t
