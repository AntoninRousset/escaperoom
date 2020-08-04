from ...event import Event


def etcd_event(event):

    from json import loads

    factory = {
        'CREATE': EtcdCreateNodeEvent,
        'MODIFY': EtcdModifyNodeEvent,
        'DELETE': EtcdDeleteNodeEvent,
    }[event.type]

    return factory(key=event.key.decode(),
                   value=loads(event.value),
                   meta=event.meta,
                   pre_value=loads(event.pre_value),
                   pre_meta=event.pre_meta,
                   revision=event.revision)


class EtcdEvent(Event):
    type = 'ETCD'


class EtcdNodeEvent(EtcdEvent):

    type = 'NODE'

    def __init__(self, key=None, value=None, meta=None, pre_value=None,
                 pre_meta=None, revision=None):

        from .accessor.selector.key import EtcdKey

        super().__init__()

        self.key = EtcdKey(key)
        self.value = value
        self.meta = meta
        self.pre_value = pre_value
        self.pre_meta = pre_meta
        self.revision = revision

    def __json__(self):
        return {
            'type': self.type,
            'key': self.key,
            'value': self.value,
            'pre_value': self.pre_value,
            'revision': self.revision,
        }


class EtcdCreateNodeEvent(EtcdNodeEvent):
    type = 'CREATE'


class EtcdModifyNodeEvent(EtcdNodeEvent):
    type = 'MODIFY'


class EtcdDeleteNodeEvent(EtcdNodeEvent):
    type = 'DELETE'
