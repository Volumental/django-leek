from .worker import Worker


def start():
    global worker_thread
    worker_thread = Worker()


def put_task(task):
    return worker_thread.put_task_on_queue(task)


def stop():
    return worker_thread.stop_thread()


def waiting():
    return worker_thread.status_waiting()


def hanled():
    return worker_thread.status_handled()
