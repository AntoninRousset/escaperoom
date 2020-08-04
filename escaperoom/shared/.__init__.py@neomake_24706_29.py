from ..event import EventSource


class EtcdAccessor(EventSource):

    def __init__(self):
        super().__init__()

    def open(self):
        return EtcdSession(self)

    async def instantiate(self):
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

    
