from .base import EtcdSelector


class EtcdGroupSelector(EtcdSelector, list):

    def __init__(self, *args):

        from . import auto

        EtcdSelector.__init__(self)
        selector = ','.join({str(sel) for sel in args})
        list.__init__(self, [auto.selector(sel)
                             for sel in selector.split(',')])

    def __str__(self):
        return ','.join(str(sel) for sel in self)

    def __contains__(self, other):

        from . import auto
        from .key import EtcdKey

        if isinstance(other, str):
            other = auto.selector(other)

        if not isinstance(other, EtcdKey):
            raise TypeError('Only etcd key allowed')

        return any(other in sel for sel in self)

    @property
    def prefix(self):

        def iter_common(*iterables):
            for row in zip(*iterables):
                if len(set(row)) == 1:
                    yield row[0]

        return ''.join(iter_common(*[str(selector) for selector in self]))

