class ContextAlreadyOpenError(Exception):
    pass


class ContextNotOpenError(Exception):
    pass


class EscaperoomContext:

    def __init__(self):

        from asyncio import Event

        self.etcd = None
        self.shared_data = None
        self.units_discovery = None
        self.quit_event = Event()

    def is_open(self):
        return self.etcd is not None

    def quit(self):
        self.quit_event.set()

    async def open(self):

        from .shared import Etcd, SharedData

        self.quit_event.clear()

        if self.is_open():
            raise ContextAlreadyOpenError()

        self.etcd = Etcd()
        await self.etcd.open()

        self.shared_data = SharedData(self.etcd)

        return self

    async def close(self):

        if not self.is_open():
            raise ContextNotOpenError()

        self.shared_data = None

        await self.etcd.close()
        self.etcd = None

    async def __aenter__(self):
        return await self.open()

    async def __aexit__(self, exc_type, exc, tb):
        return await self.close()
