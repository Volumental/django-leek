import logging
import socketserver
import threading

from . import worker_manager


log = logging.getLogger(__name__)


Dcommands = {
    'waiting': worker_manager.waiting,
    'handled': worker_manager.hanled,
    'stop': worker_manager.stop
}


class TaskSocketServer(socketserver.BaseRequestHandler):
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
                    response = worker_manager.put_task(data)
                    self.request.send(str(response).encode())
                except Exception as e:
                    log.exception("failed to queue task")
                    response = (False, "TaskServer Put: {}".format(e).encode(),)
                    self.request.send(str(response).encode())

        except OSError as e:
            # in case of network error, just log
            log.exception("network error")
