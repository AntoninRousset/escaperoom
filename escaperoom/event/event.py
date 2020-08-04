# TODO to complete
class EventType(list):

    def __str__(self):
        return '.'.join(self)

    def __repr__(self):
        return f'<{type(self).__name__} {str(self)}>'

    def __add__(self, other):

        if not isinstance(other, list):
            other = [str(other)]

        return EventType(super().__add__(self, other))

# TODO to complete
class EventMeta(type):

    def __new__(cls, name, bases, dct):

        event_bases = [b for b in bases if isinstance(b, Event)]

        if len(event_bases) > 1:
            raise ValueError('Event class can only inherit from a single '
                             'Event class')

        # the "main" Event class doesn't have a type
        if len(event_bases) == 0:
            dct['type'] = EventType()

        else:

            if 'type' not in dct:
                raise AttributeError('Missing event type')

            if isinstance(dct['type'], EventType):

                if len(dct['type']) > 1:
                    raise ValueError('Event can only be of length one')

        event = type.__new__(cls, name, bases, dct)
        return event


class Event(metaclass=EventMeta):

    def __init__(self, *args, **kwargs):
        pass

    def __repr__(self):
        return f'<{type(self).__name__} {str(self.type)}>'
