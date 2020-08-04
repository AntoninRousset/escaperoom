from ...event import EventFunnel


class EtcdAccessor(EventFunnel):

    def __init__(self, etcd):
        self.etcd = etcd
        self.add_event_source(self.etcd)


class EtcdSelectorBasedAccessor(EtcdAccessor):

    def __init__(self, etcd, sel):

        from .selector import selector

        super().__init__(etcd)
        self.selector = selector(sel)

    async def __aiter__(self):
        async for node in self.nodes:
            yield node

    @property
    def keys(self):
        return EtcdSelectorBasedKeysIterator(self)

    @property
    def values(self):
        return EtcdSelectorBasedValuesIterator(self)

    @property
    def items(self):
        return EtcdSelectorBasedItemsItemsIterator(self)

    @property
    def nodes(self):
        return EtcdSelectorBasedNodesIterator(self)

    def __repr__(self):
        return f'<{type(self).__name__} {self.selector}>'

    async def iter_selector_match(self, keys_only=False):

        for res in await self.etcd.range_prefix(self.selector.prefix,
                                                keys_only=keys_only):

            key = res if keys_only else res[0]

            if key in self.selector:
                return res

    def filter_event(self, event):
        return event.key in self.selector


class EtcdAccessorIterator:

    def __init__(self, accessor):
        self.accessor = accessor

    def __repr__(self):
        return f'<type(self).__name__ {self.accessor}>'


class EtcdSelectorBasedIterator(EtcdAccessorIterator):

    def __init__(self, accessor):

        if not isinstance(accessor, EtcdSelectorBasedAccessor):
            raise TypeError(accessor)

        super().__init__(accessor)

    def __repr__(self):
        return f'<type(self).__name__ {self.accessor.selector}>'


class EtcdSelectorBasedKeysIterator(EtcdSelectorBasedIterator):

    async def __aiter__(self):
        async for key in self.accessor.iter_selector_match(keys_only=True):
            yield key


class EtcdWildcardValuesIterator(EtcdWildcardIterator):

    async def __aiter__(self):
        async for _, value, _ in self.accessor.iter_selector_match():
            yield value


class EtcdWildcardItemsIterator(EtcdWildcardIterator):

    async def __aiter__(self):
        async for key, value, _ in self.accessor.iter_selector_match():
            yield key, value


