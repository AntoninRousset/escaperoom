from ...event import EventFunnel


class EtcdChildren(EventFunnel):

    def __init__(self, cluster, key):

        super().__init__(self)

        from .key import EtcdKey
        self.cluster = cluster
        self.key = EtcdKey(key)

    async def __aiter__(self):
        async for node in self.nodes:
            yield node

    @property
    def keys(self):
        return EtcdChildrenKeys(self)

    @property
    def values(self):
        return EtcdChildrenValues(self)

    @property
    def items(self):
        return EtcdChildrenItems(self)

    @property
    def nodes(self):
        return EtcdChildrenNodes(self)

    def __repr__(self):
        return f'<EtcdChildren {self.key}>'


class EtcdChildrenIterator:

    def __init__(self, node):
        self.node = node

    @property
    def cluster(self):
        return self.node.cluster


class EtcdChildrenKeys(EtcdChildrenIterator):

    async def __aiter__(self):
        for key in await self.cluster.ranger_prefix(self.node.key,
                                                    keys_only=True):
            if key in key.is_child_key(self.node.key):
                yield key


class EtcdChildrenValues(EtcdChildrenIterator):

    async def __aiter__(self):
        for key, value, _ in await self.cluster.ranger_prefix(self.node.key):
            if key in key.is_child_key(self.node.key):
                yield value


class EtcdChildrenItems(EtcdChildrenIterator):

    async def __aiter__(self):
        for key, value, _ in await self.cluster.ranger_prefix(self.node.key):
            if key in key.is_child_key(self.node.key):
                yield key, value


class EtcdChildrenNodes(EtcdChildrenIterator):

    async def __aiter__(self):
        from .node import EtcdNode
        for key, _, _ in await self.cluster.ranger_prefix(self.node.key):
            if key in key.is_child_key(self.node.key):
                yield EtcdNode(self.node.cluster, key)
