import logging
import socketserver
import multiprocessing

from .helpers import load_task
from . import worker
from . import helpers

log = logging.getLogger(__name__)


Dcommands = {}


class Pool(object):
    def __init__(self):
        self.queue = multiprocessing.Queue()
        self.worker = multiprocessing.Process(target=worker.target, args=(self.queue,))


class TaskSocketServer(socketserver.BaseRequestHandler):
    DEFAULT_POOL = 'default'
    # pools holds a mapping from pool names to process objects
    pools = {}

    def handle(self):
        try:
            data = self.request.recv(5000).strip()
            if data in Dcommands.keys():
                log.info('Got command: "{}"'.format(data))
                try:
                    worker_response = Dcommands[data]()
                    response = (True, worker_response.encode(),)
                    self.request.send(str(response).encode())
                except Exception as e:
                    log.exception("command failed")
                    response =  (False, "TaskServer Command: {}".format(e).encode(),)
                    self.request.send(str(response).encode())
            else:
                # assume a serialized task
                log.info('Got a task')
                try:
                    task_id = int(data.decode())
                    queued_task = load_task(task_id=task_id)
                    
                    # Ensure pool got a worker processing it
                    pool_name = queued_task.pool or self.DEFAULT_POOL
                    pool = self.pools.get(pool_name)
                    if pool is None or not pool.worker.is_alive():
                        # Spawn new pool
                        log.info('Spawning new pool: {}'.format(pool_name))
                        if pool is not None:
                            print(pool.worker.is_alive())
                        self.pools[pool_name] = Pool()
                        self.pools[pool_name].worker.start()

                    task = helpers.unpack(queued_task.pickled_task)
                    self.pools[pool_name].queue.put(task)

                    response = (True, "sent")
                    self.request.send(str(response).encode())
                except Exception as e:
                    log.exception("failed to queue task")
                    response = (False, "TaskServer Put: {}".format(e).encode(),)
                    self.request.send(str(response).encode())

        except OSError as e:
            # in case of network error, just log
            log.exception("network error")
