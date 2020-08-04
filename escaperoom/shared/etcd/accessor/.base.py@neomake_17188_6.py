from ....event import EventFunnel


class EtcdAccessor(EventFunnel):

    def __init__(self, etcd):

        super().__init__()

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
        return EtcdSelectorBasedItemsIterator(self)

    @property
    def nodes(self):
        return EtcdSelectorBasedNodesIterator(self)

    async def delete(self):
        from asyncio import gather
        await gather(*[node.delete() async for node in self.nodes])

    def __repr__(self):
        return f'<{type(self).__name__} {self.selector}>'

    async def iter_selector_match(self, keys_only=False):

        for res in await self.etcd.range_prefix(self.selector.prefix,
                                                keys_only=keys_only):

            key = res if keys_only else res[0]

            print('-->', key)

            if key in self.selector:
                print('yes')
                yield res
            else:
                print('no')

    def filter_event(self, event):
        return event.key in self.selector


class EtcdAccessorIterator:

    def __init__(self, accessor):
        self.accessor = accessor

    def __repr__(self):
        return f'<{type(self).__name__} {self.accessor}>'


class EtcdSelectorBasedIterator(EtcdAccessorIterator):

    def __init__(self, accessor):

        if not isinstance(accessor, EtcdSelectorBasedAccessor):
            raise TypeError(accessor)

        super().__init__(accessor)

    def __repr__(self):
        return f'<{type(self).__name__} {self.accessor.selector}>'


class EtcdSelectorBasedKeysIterator(EtcdSelectorBasedIterator):

    async def __aiter__(self):
        async for key in self.accessor.iter_selector_match(keys_only=True):
            yield key


class EtcdSelectorBasedValuesIterator(EtcdSelectorBasedIterator):

    async def __aiter__(self):
        async for _, value, _ in self.accessor.iter_selector_match():
            yield value


class EtcdSelectorBasedItemsIterator(EtcdSelectorBasedIterator):

    async def __aiter__(self):
        async for key, value, _ in self.accessor.iter_selector_match():
            yield key, value


class EtcdSelectorBasedNodesIterator(EtcdSelectorBasedIterator):

    async def __aiter__(self):
        from .auto import accessor
        iterator = self.accessor.iter_selector_match(keys_only=True)
        async for key, _, _ in iterator:
            yield accessor(self.accessor.etcd, key)
