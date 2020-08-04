class EventType(list):

    def __init__(self, iterable=None):

        if isinstance(iterable, str):
            iterable = [iterable]

        def check_subtype(subtype):

            subtype = str(subtype).upper()

            if '.' in subtype:
                raise ValueError('Subtype cannot contain character "."')

            return subtype

        if iterable is None:
            super().__init__()

        else:
            super().__init__(check_subtype(st) for st in iterable)

    def __str__(self):
        return '.'.join(self)

    def __repr__(self):
        return f'<{type(self).__name__} {str(self)}>'

    def __add__(self, other):

        if not isinstance(other, list):
            other = [str(other)]

        return EventType(super().__add__(other))


class EventMeta(type):

    def __new__(cls, name, bases, dct):

        event_bases = [b for b in bases if issubclass(b, Event)]

        if len(event_bases) > 1:
            raise ValueError('Event class can only inherit from a single '
                             'Event class')

        # the "main" Event class doesn't have a type
        if 'type' not in dct:
            raise AttributeError('Missing class event type')

        event_type = EventType(dct['type'])

        if len(event_type) > 1:
            raise ValueError('Event can only be of length one')

        for base in event_bases:
            dct['type'] = base.type + event_type

        event = type.__new__(cls, name, bases, dct)
        return event


class Event(metaclass=EventMeta):

    type = EventType()

    def __init__(self, *args, **kwargs):
        pass

    def __repr__(self):
        return f'<{type(self).__name__} {str(self.type)}>'

    def __json__(self):
        return {
            'type': self.type,
        }
