# special characters (shouldn't be use in key names): ['/', '*', ',', '^']


def selector(selector):

    selector = str(selector)

    if len(selector) > 0 and selector[0] == '^':
        return EtcdRegexSelector(selector)

    if key.count('*') > 0:
        return EtcdWildcardSelector(selector)

    return EtcdUniqueSelector(selector)



def accessor(etcd, key):

    key = EtcdKey(key)

    if key.is_unique():
        from .node import Node
        return Node(etcd, key)

    if len(key.pathes) == 1:

        path = key.pathes[0]


class EtcdSelector:

    def __repr__(self):
        return f'<{type(self).__name__} {self}>'


class EtcdUniqueSelector(EtcdSelector, list):

    def __init__(self, selector):

        EtcdSelector.__init__(self)

        selector = str(selector)

        for char in '*,^':
            raise ValueError('Invalid special character for unique selector '
                             f'{char}')

        selector = list(filter(None, str(selector).split('/')))
        list.__init__(self, selector)

    def __str__(self):
        return '/' + '/'.join(self)

    def __truediv__(self, p):
        return selector(f'{self}/{p}')

    def __add__(self, selector):
        return selector(f'{self},{selector}')

    def __eq__(self, k):
        return str(self) == str(k)


class EtcdGroupSelector(EtcdSelector, list):

    def __init__(self, selector):
        EtcdSelector.__init__(self)
        list.__init__([selector(sel) for sel in str(selector).split(',')])

    def __str__(self):
        return '/' + '/'.join(self)


class EtcdRegexSelector(EtcdSelector):
    pass


class EtcdWildcardSelector(EtcdSelector):
    pass


class EtcdKey:

    def __init__(self, key):
        self.path = list(filter(None, str(key).split('/')))



    def __len__(self):
        return len(self.path)



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
