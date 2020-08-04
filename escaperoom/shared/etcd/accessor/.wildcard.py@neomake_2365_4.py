from .base import EtcdSelectorBasedAccessor


class EtcdWildcardAccessor(EtcdSelectorBasedAccessor):

    async def delete(self):

        from aioetcd3 import range_prefix

        # if selector selects a single subtree
        if str(self) == f'{self.selector.prefix}**':
            prefix = str(self.selector.prefix)
            self.etcd.client.delete(self.client.delete(range_prefix(prefix)))

