class EtcdNode:

    def __init__(self, cluster, key):
        from .key import EtcdKey
        self.cluster = cluster
        self.key = EtcdKey(key)
        
    async def get_value(self):
        return await self.cluster.client.get(str(self.key))

    async def set_value(self, v):
        return await self.cluster.client.put(str(self.key), to_json(v).encode())

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
    def nodes(self):
        return EtcdNodeNodes(self)

    @property
    def subtree(self):
        return EtcdTree(self.cluster, self.key)

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
