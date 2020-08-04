class EtcdNode:

    def __init__(self, cluster, key):
        from .key import EtcdKey
        self.cluster = cluster
        self.key = EtcdKey(key)

    async def get_value(self):
        return await self.cluster.client.get(str(self.key))

    async def set_value(self, v):
        from ..misc.jsonutils import to_json
        data = to_json(v).encode()
        return await self.cluster.client.put(str(self.key), data)

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
        from .tree import EtcdTree
        return EtcdTree(self.cluster, self.key)

    async def get(self):
        from .key import EtcdKey
        from aioetcd3 import range_prefix
        subtree = await self.cluster.client.range(range_prefix(str(self.key)))
        return {(k, v, meta) for k, v, meta in subtree
                if len(EtcdKey(k)) == len(self.key) + 1}


class EtcdNodeIterator:

    def __init__(self, node):
        self.node = node


class EtcdNodeKeys(EtcdNodeIterator):

    async def __aiter__(self):
        data = {k for k, _, _ in await self.node.get()}
        for d in data:
            yield d


class EtcdNodeValues(EtcdNodeIterator):

    async def __aiter__(self):
        return (v for _, v, _ in await self.node.get())


class EtcdNodeItems(EtcdNodeIterator):

    async def __aiter__(self):
        return ((k, v) for k, v, _ in await self.node.get())


class EtcdNodeNodes(EtcdNodeIterator):

    async def __aiter__(self):
        from .node import EtcdNode
        return (EtcdNode(self.node.culster, k)
                for k, _, _ in await self.node.get())
