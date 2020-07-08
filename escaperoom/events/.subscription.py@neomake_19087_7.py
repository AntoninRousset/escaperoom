#!/usr/bin/env python
# -*- coding: utf-8 -*-

import asyncio


class Subscription:

    def __init__(self):
        self.queue = asyncio.Queue()

    async def __aiter__(self):
        return self

    async def __anext__(self):

        try:
            event = self.queue.get_nowait()

        except asyncio.QueueEmpty:
            event = await self.queue.get()

        return event

    async def emit(self, event):
        await self.queue.put(event)
