#!/usr/bin/env python
# -*- coding: utf-8 -*-

from aiohttp import web
import logging
from ...events import Event, EventSource, EventSink
from ...misc.jsonutils import to_json


logger = logging.getLogger(__name__)


class ServerSentEvent(Event):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.url = kwargs['url']
        self.event_type = kwargs['event_type']

    def __json__(self):
        return {
            'url': self.url,
            'type': self.event_type,
        }


class ServerSentEventSink(EventSink):

    def __init__(self, url, event_type):
        super().__init__()
        self.url = url
        self.event_type = event_type

    async def _read_source(self, source):
        async for event in source.subscribe():
            event = ServerSentEvent(event)
            for dest in self.destinations:
                await dest.emit(event)


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
