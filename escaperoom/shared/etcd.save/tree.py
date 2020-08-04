from .level import EtcdLevelRange


class EtcdTree(EtcdLevelRange):

    def __init__(self, cluster, key):
        super().__init__(cluster, key, start=0)

    def __repr__(self):
        return f'<EtcdTree {self.key}>'
