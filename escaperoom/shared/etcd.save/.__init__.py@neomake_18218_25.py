from ...event import EventSource
from .node import EtcdNode


class EtcdCluster(EtcdNode):

    def __init__(self, endpoint='127.0.0.1:2379'):
        from aioetcd3.client import Client

        super().__init__(self, '/')
        self.client = Client(endpoint)

    async def range_prefix(self, prefix, keys_only=False):

        from .key import EtcdKey
        from aioetcd3 import range_prefix
        from json import loads

        res = await self.client.range(range_prefix(str(prefix)),
                                      keys_only=keys_only)

        if keys_only:
            return [k.decode() for k in res]
        else:
            return [(EtcdKey(k.decode()), loads(v.decode())) for k, v, _ in res]
