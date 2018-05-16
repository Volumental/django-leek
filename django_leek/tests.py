from unittest.mock import patch
import socketserver

from django.test import TestCase
from django.core.management import call_command

@patch.object(socketserver.TCPServer, 'serve_forever')
class LeekCommandTestCase(TestCase):
    def test_leek(self, serve_forever):
        call_command('leek')
        serve_forever.assert_called()

    def test_keyboard_interrupt(self, serve_forever):
        serve_forever.side_effect = KeyboardInterrupt
        call_command('leek')
