class EtcdTree:

    def __init__(self, cluster, key):
        from .key import EtcdKey
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
        from aioetcd3 import range_prefix
        from json import loads
        tree = await self.cluster.client.range(range_prefix(str(self.key)))
        return {(k.decode(), v.decode(), meta) for k, v, meta in tree}

    def __repr__(self):
        return f'<EtcdTree {self.key}>'


class EtcdTreeIterator:

    def __init__(self, tree):
        self.tree = tree


class EtcdTreeKeys(EtcdTreeIterator):

    async def __aiter__(self):
        for key, _, _ in await self.tree.get():
            yield key


class EtcdTreeValues(EtcdTreeIterator):

    async def __aiter__(self):
        for _, value, _ in await self.tree.get():
            yield value


class EtcdTreeItems(EtcdTreeIterator):

    async def __aiter__(self):
        for key, value, _ in await self.tree.get():
            yield key, value


class EtcdTreeNodes(EtcdTreeIterator):

    async def __aiter__(self):
        from .node import EtcdNode
        for key, _, _ in await self.tree.get():
            yield EtcdNode(self.tree.culster, key)
