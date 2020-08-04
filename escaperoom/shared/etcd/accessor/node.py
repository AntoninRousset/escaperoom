from .base import EtcdSelectorBasedAccessor
from ..error import EtcdNotOpenedError


class EtcdNodeAccessor(EtcdSelectorBasedAccessor):

    def __init__(self, etcd, key):
        super().__init__(etcd, key)

    @property
    def key(self):
        return str(self.selector)

    @property
    def name(self):
        return str(self.selector).split('/')[-1]

    async def exists(self):

        try:
            await self.get()
            return True

        except KeyError:
            return False

    async def get(self):

        from json import loads

        if not self.etcd.is_open():
            raise EtcdNotOpenedError()

        key = str(self.selector).encode()
        data, _ = await self.etcd.client.get(key)

        if data is None:
            raise KeyError()

        data = data.decode()

        if data == '':
            return None
        return loads(data)

    async def set(self, value):

        from ....misc.jsonutils import to_json

        if not self.etcd.is_open():
            raise EtcdNotOpenedError()

        key = str(self.selector).encode()
        await self.etcd.client.put(key, to_json(value).encode())

    async def delete(self):

        if not self.etcd.is_open():
            raise EtcdNotOpenedError()

        key = str(self.selector).encode()
        await self.etcd.client.delete(key)

    def children(self):
        return self / '*'

    def subtree(self):
        return self / '**'

    def __truediv__(self, other):
        from .auto import accessor
        return accessor(self.etcd, self.selector / other)

    def __repr__(self):
        return f'<EtcdNode {self.selector}>'

    def filter_event(self, event):
        from .selector import selector
        return selector(event.key) == self.selector
