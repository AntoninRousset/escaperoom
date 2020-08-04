from .base import EtcdAccessor


class EtcdWildcardlAccessor(EtcdAccessor):

    def __init__(self, etcd, sel):

        from .selector import selector

        super().__init__()

        self.etcd = etcd 
        self.selector = selector(sel)

        self.add_event_source(self.etcd.root / self.selector.prefix)

    async def __aiter__(self):
        async for node in self.nodes:
            yield node

    @property
    def keys(self):
        return EtcdWildcardKeys(self)

    @property
    def values(self):
        return EtcdWildcardValues(self)

    @property
    def items(self):
        return EtcdWildcardItems(self)

    @property
    def nodes(self):
        return EtcdWildcardNodes(self)

    def __repr__(self):
        return f'<EtcdWildcard {self.selector}>'

    def filter_event(self, event):
        return event.key in self.selector

    async def iter_selector_match(self, keys_only=False):
        for res in await self.etcd.range_prefix(self.selector.prefix,
                                                keys_only=keys_only):

            key = res if keys_only else res[0]

            if key in self.selector:
                return res


class EtcdWildcardIterator:

    def __init__(self, level_range):
        self.accessor = self.accessor

class EtcdWildcardKeys(EtcdWildcardIterator):

    async def __aiter__(self):
        async for key in self.accessor.iter_selector_match(keys_only=True):
            return key


class EtcdWildcardValues(EtcdWildcardIterator):

    async def __aiter__(self):
        async for _, value, _ in self.accessor.iter_selector_match():
            yield value


class EtcdWildcardItems(EtcdWildcardIterator):

    async def __aiter__(self):

        lr = self.level_range

        for key, value, _ in await self.cluster.range_prefix(lr.key):
            if key.is_in_range(lr.key, lr.start, lr.end):
                yield key, value


class EtcdWildcardNodes(EtcdWildcardIterator):

    async def __aiter__(self):

        lr = self.level_range

        from .node import EtcdNode
        for key, _, _ in await self.cluster.range_prefix(lr.key):
            if key.is_in_range(lr.key, lr.start, lr.stop):
                yield EtcdNode(lr.cluster, key)
