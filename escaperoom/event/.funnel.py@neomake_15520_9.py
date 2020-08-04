#!/usr/bin/env python
# -*- coding: utf-8 -*-

from .source import EventSource
from asyncio import ensure_future


class EventFunnel(EventSink, EventSource):

    def __init__(self):
        EventSink.__init__(self, self)
        EventSource.__init__(self)


    async def _read_source(self, source):

        async for event in source.subscribe():
            await self.emit(event)

    def __del__(self):

        super().__del__()

        for task in self._tasks:
            task.cancel()
