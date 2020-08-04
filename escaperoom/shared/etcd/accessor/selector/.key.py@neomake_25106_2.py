from .base import EtcdSelector


# An EtcdKey is selector that for a unique element. It could have been name
# EtcdUniqueSelector but EtcdKey has been chosen to make the link with the
# original etcd nomenclature.


class EtcdKey(EtcdSelector, list):

    def __init__(self, selector):

        EtcdSelector.__init__(self)

        selector = str(selector)

        for char in '*,^':
            if char in selector:
                raise ValueError(f'Invalid special character "{char}" for key,'
                                 f' got "{selector}"')

        selector = list(filter(None, str(selector).split('/')))
        list.__init__(self, selector)

    def __str__(self):
        return '/' + '/'.join(self)

    def __truediv__(self, p):
        from . import auto
        return auto.selector(f'{self}/{p}')

    def __contains__(self, selector):
        return self == selector

    @property
    def prefix(self):
        return str(self)
