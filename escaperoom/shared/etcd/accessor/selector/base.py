class EtcdSelector:

    def __repr__(self):
        return f'<{type(self).__name__} {self}>'

    def __eq__(self, other):
        from . import auto
        other = auto.selector(other)
        return str(self) == str(other)

    def __hash__(self):
        return hash(str(self))

    def __add__(self, other):
        from . import auto
        return auto.selector(f'{self},{other}')

    @property
    def prefix(self):
        return ''

    def __json__(self):
        return str(self)
