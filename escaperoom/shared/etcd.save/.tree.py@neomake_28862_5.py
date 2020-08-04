from ...event import EventFunnel


class EtcdTree(EventFunnel):

    def __init__(self, cluster, key):

        super().__init__(self)

        from .key import EtcdKey
        self.cluster = cluster
        self.key = EtcdKey(key)

        self.add_event_source(self.cluster)

    async def __aiter__(self):
        async for node in self.nodes:
            yield node

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

    def __repr__(self):
        return f'<EtcdTree {self.key}>'


class EtcdTreeIterator:

    def __init__(self, tree):
        self.tree = tree

    @property
    def cluster(self):
        return self.tree.cluster


class EtcdTreeKeys(EtcdTreeIterator):

    async def __aiter__(self):
        for key in await self.cluster.range_prefix(self.tree.key,
                                                   keys_only=True):
            yield key


class EtcdTreeValues(EtcdTreeIterator):

    async def __aiter__(self):
        for _, value, _ in await self.cluster.range_prefix(self.tree.key):
            yield value


class EtcdTreeItems(EtcdTreeIterator):

    async def __aiter__(self):
        for key, value, _ in await self.cluster.range_prefix(self.tree.key):
            yield key, value


class EtcdTreeNodes(EtcdTreeIterator):

    async def __aiter__(self):
        from .node import EtcdNode
        for key in await self.cluster.range_prefix(self.tree.key,
                                                   keys_only=True):
            yield EtcdNode(self.cluster, key)
