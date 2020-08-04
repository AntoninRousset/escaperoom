from .base import EtcdSelector


class EtcdRegexSelector(EtcdSelector):

    def __init__(self, selector):
        super().__init__()
        self.pattern = str(selector)

    @property
    def pattern(self):
        return self._pattern

    @pattern.setter
    def pattern(self, pat):
        import re
        self.prog = re.compile(pat)
        self.pattern = pat

    def __str__(self):
        return ','.join(str(sel) for sel in self)
