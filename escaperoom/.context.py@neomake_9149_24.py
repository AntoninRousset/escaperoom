
class ContextNotOpenError(Exception):
    pass


class EscaperoomContext:

    def __init__(self):
        self.etcd = None
        self.shared_data = None

    def is_open(self):
        return self.etcd is not None

    async def open(self):

        from .shared import Etcd, SharedData

        self.etcd = Etcd()
        await self.etcd.open()

        self.shared_data = SharedData(self.etcd)

        return self

    async def close(self):

        self.shared_data = None

        await self.etcd.close()
        self.etcd = None

    async def __aenter__(self):
        return await self.open()

    async def __aexit__(self, exc_type, exc, tb):
        return await self.close
