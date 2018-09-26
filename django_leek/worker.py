#  Based on the Worker class from Python in a nutshell, by Alex Martelli
import logging

import django

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
            # workaround to solve problems with django + psycopg2
            # solution found here: https://stackoverflow.com/a/36580629/10385696
            django.db.connection.close()
            log.info('...successfully')
        except Exception as e:
            log.exception("...task failed")

    log.info('Worker stopped')
