from .key import EtcdKey
from ..event import EventSource
from ..misc.jsonutils import to_json


class EtcdTree:

    def __init__(self, cluster, key):
        self.cluster = cluster
        self.key = EtcdKey(key)

    async def __aiter__(self):
        return await self.nodes.__aiter__()

    @property
    def keys(self):
        return EtcdTreeKeys(self)

    @property
    def values(self):
        return EtcdTreeValues(self)

    @property
    def items(self):
        return EtcdTreeItems(self)

    @property
    def nodes(self):
        return EtcdTreeNodes(self)

    async def get(self):
        return await self.cluster.range(range_prefix(str(self.key)))


class EtcdTreeIterator:

    def __init__(self, tree):
        self.tree = tree


class EtcdTreeKeys(EtcdTreeIterator):

    async def __aiter__(self):
        return {k for k, _, _ in await self.tree._get()}


class EtcdTreeValues(EtcdTreeIterator):

    async def __aiter__(self):
        return {v for _, v, _ in await self.tree._get()}


class EtcdTreeItems(EtcdTreeIterator):

    async def __aiter__(self):
        return {(k, v) for k, v, _ in await self.tree._get()}


class EtcdTreeNodes(EtcdTreeIterator):

    async def __aiter__(self):
        return {EtcdNode(self.tree.culster, k)
                for k, _, _ in await self.tree._get()}
