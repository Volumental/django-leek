from django.db import models


class Task(models.Model):
    pickled_task = models.BinaryField(max_length=4096)
    pool = models.CharField(max_length=256, null=True)
    queued_on = models.DateTimeField(auto_now_add=True)
    started_at = models.DateTimeField(null=True)
    finished_at = models.DateTimeField(null=True)
    exception = models.CharField(max_length=2048, null=True)
    pickled_return = models.BinaryField(max_length=4096, null=True)
