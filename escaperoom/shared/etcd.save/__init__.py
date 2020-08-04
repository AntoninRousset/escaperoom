from .error import EtcdNotOpenedError
from ...event import EventFunnel
import logging


logger = logging.getLogger(__name__)


class Etcd(EventFunnel):

    def __init__(self, endpoint='127.0.0.1:2379'):

        super().__init__()

        self.endpoint = endpoint
        self.client = None
        self.add_event_coroutine(self._watch_etcd)

    def is_open(self):
        return self.client is not None

    async def open(self):

        from aioetcd3.client import Client

        self.client = Client(self.endpoint)

    async def close(self):
        self.client.close()
        self.client = None

    async def __aenter__(self):
        await self.open()
        return self

    async def __aexit__(self, exc_type, exc, tb):
        await self.close()

    @property
    def root(self):
        from .node import EtcdNode
        return EtcdNode(self, '/')

    async def range_prefix(self, prefix, keys_only=False):

        from .key import EtcdKey
        from aioetcd3 import range_prefix
        from json import loads

        if not self.is_open():
            raise EtcdNotOpenedError()

        res = await self.client.range(range_prefix(str(prefix)),
                                      keys_only=keys_only)

        if keys_only:
            return [EtcdKey(k.decode()) for k, _, _ in res]

        return [(EtcdKey(k.decode()), loads(v.decode()), meta)
                for k, v, meta in res]

    def convert_event(self, event):
        from .event import EtcdEvent
        return EtcdEvent(event)

    async def _watch_etcd(self):

        from asyncio import CancelledError
        from aioetcd3.help import range_prefix

        if not self.is_open():
            raise EtcdNotOpenedError()

        try:
            async for event in self.client.watch(range_prefix('')):
                await self.eat_event(event)

        # TODO good to ignore cancellation exception?
        except CancelledError:
            pass

        except BaseException:
            logger.exception('Etcd watching failed')
