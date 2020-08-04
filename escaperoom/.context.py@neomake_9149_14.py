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

    async def close(self):

        self.etcd
