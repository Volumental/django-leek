from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    help = 'Starts leek worker server'

    #def add_arguments(self, parser):
    #    parser.add_argument('poll_id', nargs='+', type=int)

    def handle(self, *args, **options):
        from django_leek import worker_manager
        from django_leek.server import TaskSocketServerThread
        import time

        worker_manager.start()
        server_thread = TaskSocketServerThread('localhost', 8002)
        time.sleep(5)
        socket_server = server_thread.socket_server()
        socket_server.serve_forever()
