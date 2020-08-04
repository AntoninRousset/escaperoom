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
        logger.debug(f'EventSink created with destination {dest}')

    def add_event_source(self, source):

        from asyncio import ensure_future

        if source in self._event_source_tasks:
            logger.warning(f'Adding an already existing event source {source} '
                           f'in {self}, ignoring')
            return

        task = ensure_future(self._read_event_source(source))
        self._event_source_tasks[source] = task

    def remove_event_source(self, source):

        if source not in self._event_source_tasks:
            logger.warning(f'Trying to remove a non-existing event source '
                           f'{source} in {self}, ignoring')
            return

        self._event_source_tasks[source].cancel()
        del self._event_source_tasks[source]

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

    def __del__(self):
        for task in self._event_source_tasks.values():
            if task:
                task.cancel()

