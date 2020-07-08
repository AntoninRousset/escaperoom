#!/usr/bin/env python
# -*- coding: utf-8 -*-

from aiohttp import web
from asyncio import Lock, Queue, ensure_future
import logging
from ...events import Event, EventSource, EventFunnel
from ...misc.jsonutils import to_json


logger = logging.getLogger(__name__)


class ServerSentEvent(EventSource):

    def __init__(self, src, event_type):
        super().__init__()
        self.src = src
        self.event_type = event_type

    def __json__(self):
        return {
            'type': self.event_type,
            'src': self.src,
        }


class ServerSentEventFunnel(EventSink):

    def __init__(self, src):
        super().__init__()
        self.src = src

    async def emit(self, event_type='update'):
        await super().emit(ServerSentEvent(self.src, event_type))


class EventsHandler(web.Application):

    def __init__(self):
        super().__init__()
        self.event_source = EventSource()
        self.router.add_get('/', self.get_events)

    def __getitem__(self, k):
        return EventSink(self)

    async def get_events(self, request):

        from aiohttp_sse import sse_response

        try:
            async with sse_response(request) as resp:
                async for event in self.event_source.subscribe():
                    await resp.send(to_json(event))

        except BaseException:
            logger.exception('get /events failed')
