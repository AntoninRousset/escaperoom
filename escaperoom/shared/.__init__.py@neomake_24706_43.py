from ..event import EventSource


class EtcdInstance(dict):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.changes = set()

    def __setitem__(self, k, v):
        self.changes.add(k)
        super().__setitem__(k, v)


class EtcdAccessor(EventSource):

    def __init__(self):
        super().__init__()

    def open(self):
        return EtcdSession(self)

    async def pull(self):
        return EtcdInstance()
    
    async def push(self):
        return EtcdInstance()






class EtcdSession:

    def __init__(self, accessor):
        self.accessor = accessor
        self.instance = None

    async def __aenter__(self):
        self.instance = self.accessor.instantiate()
        return self.instance

    async def __aexit__(self, exc_type, exc_value, traceback):
        await self.unregister()




class EtcdCluster:

    def __init__(self):
        pass

    
