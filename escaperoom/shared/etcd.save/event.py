from ...event import Event

# TODO to improve


class EtcdEvent(Event):

    def __init__(self, event_type, *, key=None, value=None, meta=None,
                 pre_value=None, pre_meta=None, revision=None):

        from .key import EtcdKey
        from json import loads
        from aioetcd3.watch import Event as Aioetcd3Event

        if isinstance(event_type, Aioetcd3Event):

            event = event_type
            self.key = EtcdKey(event.key.decode())
            if event.type == 'DELETE':
                self.value = None
            else:
                self.value = loads(event.value.decode())
            self.meta = event.meta

            # TODO failed with json.loads
            self.pre_value = event.pre_value.decode()
            self.pre_meta = event.pre_meta
            self.revision = event.revision
        else:
            self.key = key
            self.value = value
            self.meta = meta
            self.pre_value = pre_value
            self.pre_meta = pre_meta
            self.revision = revision
