#!/usr/bin/env python
# -*- coding: utf-8 -*-

from asyncio import Queue


class EventGenerator:

    def __init__(self):
        self.queue = Queue()

    async def __aiter__(self):

        from asyncio import QueueEmpty

        while True:
            try:
                event = self.queue.get_nowait()
            except QueueEmpty:
                event = await self.queue.get()
            yield event

