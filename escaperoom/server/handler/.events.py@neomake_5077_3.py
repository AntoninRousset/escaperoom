#!/usr/bin/env python
# -*- coding: utf-8 -*-

from aiohttp import web
from asyncio import Queue


class EventsHandler(web.Application):

    def __init__(self):
        super().__init__()
        self.queue = Queue()

    async def __aiter__(self):

        from asyncio import QueueEmpty

        while True:
            try:
                event = self.queue.get_nowait()
            except QueueEmpty:
                event = await self.queue.get()
            yield event

    async def new(self, src: str, event_type: str):
        await self.queue.put({
            'src': src,
            'type': event_type,
        })

    def __getitem__(self, k):
        return EventsSink(self, k)


class EventSink:

    def __init__(self, handler, src):

        from weakref import ref
        from pathlib import Path

        self._handler = ref(handler)
        self.src = Path(src)

    @property
    def handler(self):
        return self._handler()

    async def new(self, event_type='update'):
        await self.handler.new(self.src, event_type)
