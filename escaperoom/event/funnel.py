#!/usr/bin/env python
# -*- coding: utf-8 -*-

from .sink import EventSink
from .source import EventSource


class EventFunnel(EventSink, EventSource):

    def __init__(self):
        EventSink.__init__(self, self)
        EventSource.__init__(self)

    async def register_subscription(self, sub):
        self.open_event_sink()
        await super().register_subscription(sub)

    async def unregister_subscription(self, sub):
        self.close_event_sink()
        await super().unregister_subscription(sub)