from .base import EtcdSelector


# An EtcdKey is selector that for a unique element. It could have been named
# EtcdUniqueSelector but EtcdKey has been chosen to make the link with the
# original etcd nomenclature.


class EtcdKey(EtcdSelector):

    def __init__(self, selector):

        super().__init__()

        selector = str(selector)

        for char in '*,^':
            if char in selector:
                raise ValueError(f'Invalid special character "{char}" for '
                                 f'key, got "{selector}"')

        self.path = list(filter(None, str(selector).split('/')))

    def __str__(self):
        return '/' + '/'.join(self.path)

    def __truediv__(self, p):
        from . import auto
        return auto.selector(f'{self}/{p}')

    def __contains__(self, selector):
        return self == selector

    @property
    def prefix(self):
        return str(self)
