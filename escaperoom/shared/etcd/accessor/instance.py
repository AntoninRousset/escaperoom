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

    def __json__(self):
        return {
            'key': self.key,
            'value': self.value
        }


class EtcdTreeInstance(EtcdInstance):

    def __init__(self, instances, root_key='/'):

        from .selector import EtcdKey

        self.instances = {self._ensure_node_instance(kv) for kv in instances}
        self.root_key = EtcdKey(root_key)
        self.root_node = self._find_root_node(self.instances, self.root_key)

    def __iter__(self):

        def iter_children():

            root_len = len(self.root_key.path)
            children_names = {inst.key.path[root_len]
                              for inst in self.instances
                              if len(inst.key.path) > root_len}

            for name in children_names:
                root_key = self.root_key / name
                subtree = root_key / '**'
                instances = {inst for inst in self.instances
                             if inst.key in subtree}
                yield EtcdTreeInstance(instances, root_key=root_key)

        return iter_children()

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

    def __repr__(self):
        return f'<{type(self).__name__} {self.root_key}>'

    def __hash__(self):
        return hash(self.root_key)

    def __json__(self):
        return {
            'key': self.root_key,
            'node': self.root_node,
            'children': {inst.root_key.path[-1]: inst for inst in self},
        }
