from ..event import EventSource


class EtcdInstance(dict):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class EtcdAccessor(EventSource):

    def __init__(self):
        super().__init__()

    def open(self):
        return EtcdSession(self)

    async def pull(self):
        return EtcdInstance()

    async def push(self, instance):
        pass



class EtcdSession:

    def __init__(self, accessor):
        self.accessor = accessor
        self.instance = None

    async def __aenter__(self):
        self.instance = self.accessor.pull()
        return self.instance

    async def __aexit__(self, exc_type, exc_value, traceback):
        if self.instance is not None:
            await self.accessor.push(self.insance)




class EtcdCluster:

    def __init__(self):
        pass

    
