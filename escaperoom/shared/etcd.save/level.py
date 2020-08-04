from ...event import EventFunnel


# TODO better name than "range" ?

class EtcdLevelRange(EventFunnel):

    def __init__(self, cluster, key, start, end=None):

        from .key import EtcdKey

        super().__init__()

        self.cluster = cluster
        self.key = EtcdKey(key)
        self.start = start
        self.end = end

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
        res = EtcdKey(event.key).is_in_range(self.key, self.start, self.end)
        #print(event.key, self.key, res)
        return res


class EtcdLevelRangeIterator:

    def __init__(self, level_range):
        self.level_range = level_range

    @property
    def cluster(self):
        return self.level_range.cluster


class EtcdLevelRangeKeys(EtcdLevelRangeIterator):

    async def __aiter__(self):

        lr = self.level_range

        for key in await self.cluster.range_prefix(lr.key, keys_only=True):
            if key.is_in_range(lr.key, lr.start, lr.end):
                yield key


class EtcdLevelRangeValues(EtcdLevelRangeIterator):

    async def __aiter__(self):

        lr = self.level_range

        for key, value, _ in await self.cluster.range_prefix(lr.key):
            if key.is_in_range(lr.key, lr.start, lr.end):
                yield value


class EtcdLevelRangeItems(EtcdLevelRangeIterator):

    async def __aiter__(self):

        lr = self.level_range

        for key, value, _ in await self.cluster.range_prefix(lr.key):
            if key.is_in_range(lr.key, lr.start, lr.end):
                yield key, value


class EtcdLevelRangeNodes(EtcdLevelRangeIterator):

    async def __aiter__(self):

        lr = self.level_range

        from .node import EtcdNode
        for key, _, _ in await self.cluster.range_prefix(lr.key):
            if key.is_in_range(lr.key, lr.start, lr.stop):
                yield EtcdNode(lr.cluster, key)
