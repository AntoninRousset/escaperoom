from ...event import EventFunnel
from ...misc.asyncutils import classtask
import logging


logger = logging.getLogger(__name__)


class EtcdNotOpenedError(Exception):
    pass


class Etcd(EventFunnel):

    def __init__(self, endpoint='127.0.0.1:2379'):

        super().__init__()

        self.endpoint = endpoint
        self.client = None
        self._watch_etcd_task = None

    async def open(self):

        from aioetcd3.client import Client
        from asyncio import ensure_future

        self.client = Client(self.endpoint)
        self._watch_etcd_task = ensure_future(self._watch_etcd())

    async def close(self):
        self.client.close()
        self.client = None
        self._watch_etcd.cancel()
        self._watch_etcd = None

    async def __aenter__(self):
        await self.open()

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

        if self.client is None:
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

    @classtask
    async def _watch_etcd(self):

        from aioetcd3.help import range_prefix

        if self.client is None:
            raise EtcdNotOpenedError()

        try:
            async for event in self.client.watch(range_prefix('')):

                if self.filter_event(event):
                    event = self.convert_event(event)

                    for dest in self.destinations:
                        try:
                            await dest.emit_event(event)

                        except BaseException:
                            logger.exception(f'Event emission to dest {dest} '
                                             'failed')

        except BaseException:
            logger.exception('Etcd watching failed')
