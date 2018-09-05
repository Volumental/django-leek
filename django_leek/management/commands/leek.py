import socketserver

from django.core.management.base import BaseCommand, CommandError
from django.conf import settings

from django_leek.server import TaskSocketServer


def _endpoint(endpoint):
    host, port = endpoint.split(':')
    return host, int(port)


class Command(BaseCommand):
    help = 'Starts leek worker server'

    #def add_arguments(self, parser):
    #    parser.add_argument('poll_id', nargs='+', type=int)

    def handle(self, *args, **options):
        try:
            cfg = getattr(settings, 'LEEK', {})
            host, port = _endpoint(cfg.get('bind', 'localhost:8002'))

            print('Listening on {port}'.format(port=port))
            socketserver.TCPServer.allow_reuse_address = True
            server = socketserver.TCPServer((host, port), TaskSocketServer)
            server.serve_forever()
        except KeyboardInterrupt:
            pass
        print('exiting')
