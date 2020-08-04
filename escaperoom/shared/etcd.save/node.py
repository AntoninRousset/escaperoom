from .level import EtcdLevelRange
from .error import EtcdNotOpenedError
from ...event import EventFunnel


class EtcdNode(EventFunnel):

    def __init__(self, cluster, key):

        from .key import EtcdKey

        super().__init__()

        self.cluster = cluster
        self.key = EtcdKey(key)

        self.add_event_source(self.cluster)

    async def exists(self):

        try:
            await self.get()
            return True

        except KeyError:
            return False

    async def get(self):

        from json import loads

        if not self.cluster.is_open():
            raise EtcdNotOpenedError()

        key = str(self.key).encode()
        data, _ = await self.cluster.client.get(key)

        if data is None:
            raise KeyError()

        return loads(data.decode())

    async def set(self, v):

        from ...misc.jsonutils import to_json

        if not self.cluster.is_open():
            raise EtcdNotOpenedError()

        key = str(self.key).encode()
        data = to_json(v).encode()
        await self.cluster.client.put(key, data)

    async def delete(self):

        if not self.cluster.is_open():
            raise EtcdNotOpenedError()

        key = str(self.key).encode()
        await self.cluster.client.delete(key)

    def level_range(self, start, end=None):
        return EtcdLevelRange(self.cluster, self.key, start, end)

    def children(self):
        return EtcdLevelRange(self.cluster, self.key, start=1, end=2)

    def subtree(self):
        return EtcdLevelRange(self.cluster, self.key, start=0)

    def __truediv__(self, p):
        return EtcdNode(self.cluster, self.key / p)

    def __repr__(self):
        return f'<EtcdNode {self.key}>'

    def filter_event(self, event):
        from .key import EtcdKey
        return EtcdKey(event.key) == self.key
