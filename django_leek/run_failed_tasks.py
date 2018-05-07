import pickle
import base64
import os
import sys

# environ settings variable, should be the same as in manage.py
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "mysite.settings")
os.environ["DJANGO_SETTINGS_MODULE"] = "mysite.settings"
import django
django.setup()

 
# edit to the correct mysite.tasks_queue path
from .models import FailedTasks, QueuedTasks


Lfailed_tasks_id = FailedTasks.objects.values_list("task_id", flat=True)
tasks = QueuedTasks.objects.filter(pk__in=Lfailed_tasks_id)
for r in tasks:
    task = pickle.loads(base64.b64decode(r.pickled_task))
    task.run()
