from .wildcard import EtcdWildcardSelector


class EtcdChildrenSelector(EtcdWildcardSelector):

    def __init__(self, selector):

        super().__init__(selector)

        if str(self).count('*') != 1 or len(self) == 0 or str(self)[-1] != '*':
            raise ValueError('Children selector must have exactly one '
                             'wildcard at the end.')

        for i, name in enumerate(self):
            if name.count('**') > 0:
                raise ValueError('Children selector should not contain '
                                 'subtree wildcard "**", got "{str(self)}"')

    def __contains__(self, other):

        from . import auto
        from .unique import EtcdUniqueSelector

        if isinstance(other, str):
            other = auto.selector(other)

        if not isinstance(other, EtcdUniqueSelector):
            raise TypeError('Only unique selector allowed')

        return self.prog.match(str(other)) is not None
