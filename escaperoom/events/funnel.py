#!/usr/bin/env python
# -*- coding: utf-8 -*-

from .sink import EventSink
from .source import EventSource


class EventFunnel(EventSink, EventSource):

    def __init__(self):
        EventSink.__init__(self, self)
        EventSource.__init__(self)
