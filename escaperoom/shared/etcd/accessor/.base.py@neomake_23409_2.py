from ...event import EventFunnel


class EtcdAccessor(EventFunnel):

    def __init__(self, etcd):
        self.etcd = etcd



