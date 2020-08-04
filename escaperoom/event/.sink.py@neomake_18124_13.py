import logging

logger = logging.getLogger(__name__)

class EventSink:

    def __init__(self, dest):

        super().__init__()

        try:
            self.destinations = set(dest)

        except TypeError:
            self.destinations = {dest}

        self.events_sources = set()
        self._event_source_reading_tasks = set()

    def add_event_source(self, source):

        from asyncio import ensure_future

        self.events_sources.add(source)
        if self.event_subscriptions:
            self._event_source_reading_tasks.add(ensure_future(self._read_event_source(source)))

    async def _read_event_source(self, source):

        try:
            async with source.subscribe() as sub:

                async for event in sub:

                    if self.filter_event(event):
                        event = self.convert_event(event)

                        for dest in self.destinations:
                            try:
                                await dest.emit_event(event)

                            except BaseException:
                                logger.exception('Event emission to dest '
                                                 f'{dest} failed')

        except BaseException:
            logger.exception('Event source reading failed')

    def filter_event(self, event):
        return True

    def convert_event(self, event):
        return event

    def __del__(self):

        for task in self._tasks:
            task.cancel()
