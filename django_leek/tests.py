from unittest.mock import patch
import socketserver

from django.test import TestCase
from django.core.management import call_command

class LeekCommandTestCase(TestCase):
    @patch.object(socketserver.TCPServer, 'serve_forever')
    def test_leek(self, serve_forever):
        call_command('leek')
        serve_forever.assert_called()
