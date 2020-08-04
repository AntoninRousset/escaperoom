class EtcdNode:

    def __init__(self, cluster, key):
        from .key import EtcdKey
        self.cluster = cluster
        self.key = EtcdKey(key)

    async def get_value(self):
        from json import loads
        key = str(self.key).encode()
        data, _ = await self.cluster.client.get(key)
        return loads(data.decode())

    async def set_value(self, v):
        from ...misc.jsonutils import to_json
        key = str(self.key).encode()
        data = to_json(v).encode()
        await self.cluster.client.put(key, data)

    async def __aiter__(self):
        async for node in self.nodes:
            yield node

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
        return {(k, v, meta) for k, v, meta in await self.subtree.get()
                if len(EtcdKey(k)) == len(self.key) + 1}

    def __truediv__(self, p):
        return type(self)(self.key / p)


    def __repr__(self):
        return f'<EtcdNode {self.key}>'


class EtcdNodeIterator:

    def __init__(self, node):
        self.node = node


class EtcdNodeKeys(EtcdNodeIterator):

    async def __aiter__(self):
        for key, _, _ in await self.node.get():
            yield key


class EtcdNodeValues(EtcdNodeIterator):

    async def __aiter__(self):
        for _, value, _ in await self.node.get():
            yield value


class EtcdNodeItems(EtcdNodeIterator):

    async def __aiter__(self):
        for key, value, _ in await self.node.get():
            yield key, value


class EtcdNodeNodes(EtcdNodeIterator):

    async def __aiter__(self):
        from .node import EtcdNode
        for key, _, _ in await self.node.get():
            yield EtcdNode(self.node.cluster, key)
