class EtcdNode:

    def __init__(self, cluster, key):
        from .key import EtcdKey
        self.cluster = cluster
        self.key = EtcdKey(key)

    async def __aiter__(self):
        return await self.nodes.__aiter__()

    @property
    def keys(self):
        return EtcdNodeKeys(self)

    @property
    def values(self):
        return EtcdNodeValues(self)

    @property
    def items(self):
        return EtcdNodeItems(self)

    @property
    def subnodes(self):
        return EtcdNodeSubnodes(self)

    async def get(self):
        from aioetcd3 import range_prefix
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
        from .node import EtcdNode
        return {EtcdNode(self.tree.culster, k)
                for k, _, _ in await self.tree._get()}
