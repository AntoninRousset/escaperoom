import logging


logger = logging.getLogger(__name__)


class EventSink:

    def __init__(self, dest):

        super().__init__()

        try:
            self.destinations = set(dest)

        except TypeError:
            self.destinations = {dest}

        self._sink_coroutines = set()
        self._sink_tasks = None

        logger.debug(f'EventSink created')

    async def open_event_sink(self):
        from asyncio import ensure_future
        self._sink_tasks = {ensure_future(coro())
                            for coro in self_sink_coroutines}

    async def close_event_sink(self):
        pass

    def add_event_coroutine(self, coroutine_func):
        self._sink_coroutines.add(coroutine_func)

    def add_event_source(self, source):

        async def read_source():
            await self._read_event_source(source)

        self.add_event_coroutine(read_source)

    async def eat_event(self, event):

        if self.filter_event(event):
            event = self.convert_event(event)

            for dest in self.destinations:
                try:
                    await dest.emit_event(event)

                except BaseException:
                    logger.exception('Event emission to dest '
                                     f'{dest} failed')

    def filter_event(self, event):
        return True

    def convert_event(self, event):
        return event

    async def _read_event_source(self, source):

        try:
            async with source.subscribe() as sub:
                async for event in sub:
                    await self.eat_event(event)

        except BaseException:
            logger.exception('Event source reading failed')
