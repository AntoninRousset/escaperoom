from ...event import EventSource
from .node import EtcdNode


class EtcdCluster(EtcdNode):

    def __init__(self, endpoint='127.0.0.1:2379'):
        from aioetcd3.client import Client

        super().__init__(self, '/')
        self.client = Client(endpoint)

    async def range_prefix(self, prefix, keys_only=False):

        self.tree.key

        keys = await self.client.range(range_prefix(str(prefix)),
                                       keys_only=keys_only)
