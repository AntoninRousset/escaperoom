from .regex import EtcdSelector


class EtcdChildrenSelector(EtcdSelector, list):

    def __init__(self, selector):

        selector = str(selector)

        for char in ',^':
            raise ValueError('Invalid special character for unique selector '
                             f'{char}')

        selector = list(filter(None, str(selector).split('/')))
        list.__init__(self, selector)

        if str(self).count('*') != 1 or len(self) == 0 or str(self)[-1] != '*':
            raise ValueError('Children selector must have exactly one '
                             'wildcard at the end.')


        for i, name in enumerate(self):

            if name.count('**') > 0:
                raise ValueError('Children selector should not contain '
                                 'subtree wildcard "**", got "{str(self)}"')


    def __str__(self):
        return '/' + '/'.join(self)

    def __truediv__(self, p):
        from . import auto
        return auto.selector(f'{self}/{p}')
