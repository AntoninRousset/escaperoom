import asyncio


class Subscription:

    def __init__(self, source):
        self.queue = asyncio.Queue()
        self.source = source

    async def register(self):
        await self.source.register_subscription(self)

    async def unregister(self):
        await self.source.unregister_subscription(self)

    async def __aenter__(self):
        await self.register()
        return self

    async def __aexit__(self, exc_type, exc_value, traceback):
        await self.unregister()

    def __aiter__(self):
        return self

    async def __anext__(self):

        try:
            return self.queue.get_nowait()

        except asyncio.QueueEmpty:
            return await self.queue.get()

    async def emit_event(self, event):
        await self.queue.put(event)
