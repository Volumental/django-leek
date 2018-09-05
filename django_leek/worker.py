#  Based on the Worker class from Python in a nutshell, by Alex Martelli
import logging
import os
import sys
import threading
import queue


import django


from . import settings
from . import helpers


log = logging.getLogger(__name__)


def target(queue):
    django.setup()
    log.info('Worker Starts')
    done = False
    while not done:
        try:
            task = queue.get()
            if task is None:
                done = True
                break
                
            log.info('running task...')
            task()
            #helpers.save_task_success(task)
            log.info('...successfully')
        except Exception as e:
            log.exception("...task failed")

    log.info('Worker stopped')
