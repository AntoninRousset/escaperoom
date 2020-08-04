from ...event import EventFunnel


# TODO better name than "range" ?

class EtcdLevelRange(EventFunnel):

    def __init__(self, cluster, key, start, end=None):

        super().__init__()

        from .key import EtcdKey
        self.cluster = cluster
        self.key = EtcdKey(key)

        self.add_event_source(self.cluster)

    async def __aiter__(self):
        async for node in self.nodes:
            yield node

    @property
    def keys(self):
        return EtcdLevelRangeKeys(self)

    @property
    def values(self):
        return EtcdLevelRangeValues(self)

    @property
    def items(self):
        return EtcdLevelRangeItems(self)

    @property
    def nodes(self):
        return EtcdLevelRangeNodes(self)

    def __repr__(self):
        return f'<EtcdLevelRange {self.key} [{self.start}, {self.end}]>'

    def filter_event(self, event):
        from .key import EtcdKey
        return EtcdKey(event.key).is_in_range(self.key, self.start, self.end)


class EtcdLevelRangeIterator:

    def __init__(self, level_range):
        self.level_range = level_range

    @property
    def cluster(self):
        return self.level_range.cluster


class EtcdLevelRangeKeys(EtcdLevelRangeIterator):

    async def __aiter__(self):
        for key in await self.cluster.range_prefix(self.level_range.key,
                                                   keys_only=True):
            if key.is_in_range(self.level_range.key, self.level_range.start,
                               self.level_range.end):
                yield key


class EtcdLevelRangeValues(EtcdLevelRangeIterator):

    async def __aiter__(self):

        key = self.level_range.key

        for key, value, _ in await self.cluster.range_prefix(key):
            if key.is_in_range(self.node.key, self.start, self.end):
                yield value


class EtcdLevelRangeItems(EtcdLevelRangeIterator):

    async def __aiter__(self):
        for key, value, _ in await self.cluster.range_prefix(self.node.key):
            if key.is_in_range(self.node.key, self.start, self.end):
                yield key, value


class EtcdLevelRangeNodes(EtcdLevelRangeIterator):

    async def __aiter__(self):
        from .node import EtcdNode
        for key, _, _ in await self.cluster.range_prefix(self.node.key):
            if key.is_in_range(self.node.key):
                yield EtcdNode(self.node.cluster, key)
