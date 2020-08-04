from ...event import EventFunnel
import logging

logger = logging.getLogger(__name__)


class EtcdCluster(EventFunnel):

    def __init__(self, endpoint='127.0.0.1:2379'):
        from aioetcd3.client import Client
        from asyncio import ensure_future

        super().__init__()

        self.client = Client(endpoint)
        self._tasks.add(ensure_future(self._watch_etcd()))

    @property
    def root(self):
        from .node import EtcdNode
        return EtcdNode(self, '/')

    async def range_prefix(self, prefix, keys_only=False):

        from aioetcd3 import range_prefix
        from json import loads

        res = await self.client.range(range_prefix(str(prefix)),
                                      keys_only=keys_only)

        if keys_only:
            return [k.decode() for k, _, _ in res]
        else:
            from .key import EtcdKey
            return [(EtcdKey(k.decode()), loads(v.decode()), meta)
                    for k, v, meta in res]

    async def _watch_etcd(self):

        from aioetcd3.help import range_prefix

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
