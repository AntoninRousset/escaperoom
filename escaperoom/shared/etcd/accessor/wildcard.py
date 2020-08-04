from .base import EtcdSelectorBasedAccessor


class EtcdWildcardAccessor(EtcdSelectorBasedAccessor):

    async def delete(self):

        from aioetcd3 import range_prefix

        # if selector selects a single subtree, the whole subtree can be
        # deleted faster using a range_prefix
        if str(self.selector) == f'{self.selector.prefix}**':
            prefix = str(self.selector.prefix)
            await self.etcd.client.delete(range_prefix(prefix))

        else:
            await super().delete()

    def __truediv__(self, other):
        from .auto import accessor
        return accessor(self.etcd, self.selector / other)
