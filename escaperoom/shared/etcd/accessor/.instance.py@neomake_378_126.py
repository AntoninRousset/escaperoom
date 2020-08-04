class EtcdInstance:
    pass


class EtcdNodeInstance(EtcdInstance):

    def __init__(self, key, value=None):

        from .selector import EtcdKey

        super().__init__()

        self.key = EtcdKey(key)
        self.value = value

    def __repr__(self):
        return f'<{type(self).__name__} {self.key} {repr(self.value)}>'

    def __hash__(self):
        return hash(self.key)

    def __eq__(self, other):
        if not isinstance(other, EtcdNodeInstance):
            raise TypeError('Can only be compared to other EtcdNodeInstance')
        return (self.key == other.key) 


class EtcdTreeInstance(EtcdInstance):

    def __init__(self, instances, root_key='/'):

        from .selector import EtcdKey

        self.instances = {self._ensure_node_instance(kv) for kv in instances}
        self.root_key = EtcdKey(root_key)
        self.root_node = self._find_root_node(instances, root_key)

    def __iter__(self):

        root_len = len(self.root_key)
        children_names = {inst.key[root_len] for inst in self.instances
                          if len(inst.key) > root_len}

    @staticmethod
    def _ensure_node_instance(kv):

        if isinstance(kv, EtcdNodeInstance):
            return kv

        if isinstance(kv, tuple):
            return EtcdNodeInstance(*kv)

        return EtcdNodeInstance(kv)

    @staticmethod
    def _find_root_node(instances, root_key):
        for inst in instances:
            if inst.key == root_key:
                return inst



        EtcdInstance.__init__(self)
        set.__init__(self, {ensure_node_instance(kv) for kv in keys_or_map})

        self.root, self.rootnode = self._find_common_parent()

    @property
    def children(self):

        from itertools import groupby

        prefix_len = len(self.root)
        children = filter(lambda node: len(node.key) > prefix_len, self)
        groups = groupby(children, key=lambda node: node.key[prefix_len])
        return {EtcdTreeInstance(v) for _, v in groups}

    @property
    def keys(self):
        return {inst.key for inst in self}

    @property
    def values(self):
        return {inst.value for inst in self}

    def _find_common_parent(self):

        from .selector import EtcdKey

        prefix = []
        for row in zip(*self.keys):
            if len(set(row)) != 1:
                break
            prefix += [row[0]]

        prefix = EtcdKey('/'.join(prefix))

        for node in self:
            if node.key == prefix:
                return prefix, node
        return prefix, None

    def __repr__(self):
        return f'<{type(self).__name__} {self.root}>'

    def __hash__(self):
        return hash(self.root)