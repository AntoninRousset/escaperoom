#!/usr/bin/env python
# -*- coding: utf-8 -*-

from aiohttp import web
import logging
from ...event import Event, EventSource, EventSink
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

    def __init__(self, dest, url, event_type):
        super().__init__(dest)
        self.url = url
        self.event_type = event_type

    def convert(self, event):
        return ServerSentEvent(event, url=self.url, event_type=self.event_type)


class EventsHandler(web.Application):

    def __init__(self):
        super().__init__()
        self.event_source = EventSource()
        self.router.add_get('', self.get_events)

    def __getitem__(self, k):
        return ServerSentEventSink(self.event_source, k, event_type='update')

    async def get_events(self, request):

        from asyncio import CancelledError
        from aiohttp_sse import sse_response

        try:
            print('## new sse ##')
            async with sse_response(request) as resp:
                async for event in self.event_source:
                    print('** Sending', event)
                    await resp.send(to_json(event))

        except CancelledError:
            print('## stop sse ##')

        except BaseException:
            logger.exception('get /events failed')
