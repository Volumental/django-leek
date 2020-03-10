import base64
import pickle
from typing import Any

from django.db import models


class Task(models.Model):
    pickled_task = models.BinaryField(max_length=4096)
    pool = models.CharField(max_length=256, null=True)
    queued_at = models.DateTimeField(auto_now_add=True)
    started_at = models.DateTimeField(null=True)
    finished_at = models.DateTimeField(null=True)
    pickled_exception = models.BinaryField(max_length=2048, null=True)
    pickled_return = models.BinaryField(max_length=4096, null=True)

    @property
    def exception(self):
        if self.pickled_exception is None:
            return None
        return pickle.loads(base64.b64decode(self.pickled_exception))

    @property
    def return_value(self):
        if self.pickled_return is None:
            return None
        return pickle.loads(base64.b64decode(self.pickled_return))

    def started(self) -> bool:
        return self.started_at is not None

    def finished(self) -> bool:
        return self.finished_at is not None

    def successful(self) -> bool:
        return self.finished() and self.pickled_return is not None
