from .source import EventSource
from asyncio import ensure_future


class EventSink:

    def __init__(self, dest):


        super().__init__()

        try:
            self.dest = set(dest)

        except TypeError:
            self.dest = {dest}

        self._tasks = set()

    def add_source(self, source):
        self._tasks.add(ensure_future(self._read_source(source)))

    async def _read_source(self, source):

        async for event in source.subscribe():
            await self.emit(event)

    def __del__(self):

        super().__del__()

        for task in self._tasks:
            task.cancel()
