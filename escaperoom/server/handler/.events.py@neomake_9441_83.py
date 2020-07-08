#!/usr/bin/env python
# -*- coding: utf-8 -*-

from aiohttp import web
from asyncio import Lock, Queue, ensure_future
import logging
from . import to_json


logger = logging.getLogger(__name__)


class Subscription:

    def __init__(self, source):
        self.queue = Queue()

    async def __aiter__(self):
        pass


class EventSource:

    def __init__(self):
        self.lock = Lock()
        self.subscriptions = set()

    async def subscribe(self):

        from weakref import ref

        sub = Subscription(self)
        async with self.lock:
            self.subscriptions.add(ref(sub))

        return sub

    async def clean_up(self):

        self.sub


class EventsSink:

    def __init__(self, handler, src):

        from weakref import ref
        from pathlib import Path

        self._handler = ref(handler)
        self.src = Path(src)
        self._tasks = set()

        self.router.add_get('/', self.get_events)

    @property
    def handler(self):
        return self._handler()

    def add_source(self, source):
        self._tasks.add(ensure_future(self._read_source(source)))

    async def new(self, event_type='update'):
        await self.handler.new(self.src, event_type)

    async def _read_source(self, source, event_type='update'):

        async for event in source:
            await self.new(event_type)

    def __del__(self):
        for task in self._tasks:
            task.cancel()


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

    async def get_events(self, request):

        from aiohttp_sse import sse_response

        try:
            async with sse_response(request) as resp:
                async for event in self:
                    await resp.send(to_json(event))

        except BaseException:
            logger.exception('get /events failed')
