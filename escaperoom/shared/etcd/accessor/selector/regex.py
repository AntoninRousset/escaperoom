from .base import EtcdSelector


class EtcdRegexSelector(EtcdSelector):

    def __init__(self, selector):
        EtcdSelector.__init__(self)
        self.pattern = str(selector)

    @property
    def pattern(self):
        return self._pattern

    @pattern.setter
    def pattern(self, pat):
        import re
        self.prog = re.compile(pat)
        self._pattern = pat

    def __str__(self):
        return self.pattern

    def __contains__(self, other):

        from . import auto
        from .key import EtcdKey

        if isinstance(other, str):
            other = auto.selector(other)

        if not isinstance(other, EtcdKey):
            raise TypeError('Only key allowed')

        return self.prog.match(str(other)) is not None
