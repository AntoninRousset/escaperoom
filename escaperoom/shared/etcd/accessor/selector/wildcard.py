from .regex import EtcdRegexSelector


class EtcdWildcardSelector(EtcdRegexSelector, list):

    def __init__(self, selector):

        selector = str(selector)

        for char in ',^':
            if char in selector:
                raise ValueError(f'Invalid special character "{char}" for '
                                 f'wildcard selector, got "{selector}"')

        list.__init__(self, list(filter(None, str(selector).split('/'))))

        for i, name in enumerate(self):

            if '**' in name and name != '**':
                raise ValueError('Invalid use of subtree wildcard "**", got '
                                 f'"{str(selector)}"')

            if name == '**' and i + 1 < len(self):
                raise ValueError('Use of subtree wildcard "**" can only be '
                                 'used at the end of the selector, got '
                                 f'"{str(selector)}"')

        pattern = str(self)
        if pattern.endswith('/**'):
            pat = pattern[:-3].replace('*', '[^/]+')
            pattern = f'(^{pat}$)|(^{pat}/.*$)'
        else:
            pattern = '^' + pattern.replace('*', '[^/]+') + '$'

        EtcdRegexSelector.__init__(self, pattern)

    def __str__(self):
        return '/' + '/'.join(self)

    def __truediv__(self, p):
        from . import auto
        return auto.selector(f'{self}/{p}')

    @property
    def prefix(self):
        return str(self).split('*')[0]
