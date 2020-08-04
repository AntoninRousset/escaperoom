

class EventSink:

    def __init__(self, dest):

        super().__init__()

        try:
            self.destinations = set(dest)

        except TypeError:
            self.destinations = {dest}

        self._tasks = set()

    def add_event_source(self, source):
        from asyncio import ensure_future
        self._tasks.add(ensure_future(self._read_event_source(source)))

    async def _read_event_source(self, source):

        async with source.subscription as sub:
            async for event in sub:

                event = self.convert(event)

                for dest in self.destinations:
                    await dest.emit_event(event)

    def convert_event(self, event):
        return event

    def filter_event(self, event):
        return event

    def __del__(self):
        for task in self._tasks:
            task.cancel()
