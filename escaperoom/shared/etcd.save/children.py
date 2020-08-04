from .level import EtcdLevelRange


class EtcdChildren(EtcdLevelRange):

    def __init__(self, cluster, key):
        super().__init__(self.cluster, start=1, end=2)

    def __repr__(self):
        return f'<EtcdChildren {self.key}>'
