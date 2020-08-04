# special characters (shouldn't be use in key names): ['/', '*', ',', '^']


def selector(sel):

    sel = str(sel)

    if len(sel) > 0 and sel[0]:
        return RegexEtcdSelector(sel)

    if key.count('*') > 0:
        return WildcardEtcdSelector(sel)


def accessor(etcd, key):

    key = EtcdKey(key)

    if key.is_unique():
        from .node import Node
        return Node(etcd, key)

    if len(key.pathes) == 1:

        path = key.pathes[0]

        if path.count('*') == 1 and path[-1] == '*':
            return 
        





class EtcdKey:

    def __init__(self, key):
        self.path = list(filter(None, str(key).split('/')))

    def __truediv__(self, p):
        return EtcdKey(f'{self}/{p}')

    def __str__(self):
        return '/' + '/'.join(self.path)

    def __len__(self):
        return len(self.path)

    def __eq__(self, k):
        return str(self) == str(k)

    def __repr__(self):
        return f'<EtcdKey {self}>'

    def __contains__(self, p):
        return str(p).startswith(str(self))

    def is_in_range(self, p, start, end=None):

        p = EtcdKey(p)

        if self not in p:
            return False

        if end is not None and len(self) >= len(p) + end:
            return False

        if len(self) < len(p) + start:
            return False

        return True
