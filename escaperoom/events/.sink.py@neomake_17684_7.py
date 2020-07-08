from asyncio import ensure_future


class EventSink:

    def __init__(self, dest):

        super().__init__()

        try:
            self.destinations = set(dest)

        except TypeError:
            self.destinations = {dest}

        self._tasks = set()

    def add_source(self, source):
        self._tasks.add(ensure_future(self._read_source(source)))

    async def _read_source(self, source):
        async for event in source.subscribe():
            for dest in self.destinations:
                await dest.emit(event)

    def __del__(self):
        for task in self._tasks:
            task.cancel()
