from django.test import TestCase
from channels.testing import WebsocketCommunicator
from network import consumers


class NodeConsumerTest(TestCase):
    async def test_attribute_write(self):
        path = 'node/'
        communicator = WebsocketCommunicator(consumers.NodeConsumer, path)
