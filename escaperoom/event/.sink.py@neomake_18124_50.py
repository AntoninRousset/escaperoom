import logging

logger = logging.getLogger(__name__)

class EventSink:

    def __init__(self, dest):

        super().__init__()

        try:
            self.destinations = set(dest)

        except TypeError:
            self.destinations = {dest}

        self._event_source_tasks = dict()

    def add_event_source(self, source):

        if source in self._event_source_tasks:
            return

        self._event_source_tasks[source] = None

        if self.event_subscriptions:
            self.start_event_source(source)

    def remove_event_source(self, source):

        if source in self._event_source_tasks:
            self.stop_event_source(source)

        del self._event_source_tasks[source]

    def start_reading_event_source(self, source):

        from asyncio import ensure_future

        # check if not already running
        if self._event_source_tasks.get(source) is not None:
            return

        future = ensure_future(self._read_event_source(source))
        self._event_source_tasks[source] = future

    def stop_reading_event_source(self, source):

        if self._event_source_tasks.get(source) is None:
            return

        self._event_source_tasks[source].cancel()





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
