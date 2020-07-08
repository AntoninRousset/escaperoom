#!/usr/bin/env python
# -*- coding: utf-8 -*-

from asyncio import Lock


class EventSource:

    def __init__(self):
        self.lock = Lock()
        self.subscriptions = set()

    async def __aiter__(self):

        from .subscription import Subscription
        from weakref import ref

        sub = Subscription()

        async with self.lock:
            self.subscriptions.add(ref(sub))

        return sub

    async def clean_up(self):

        async with self.lock:
            self.subscriptions = {ref for ref in self.subscriptions
                                  if ref() is not None}

    async def emit(self, event):

        async with self.lock:
            for sub_ref in self.subscriptions:

                sub = sub_ref()

                if sub is not None:
                    await sub.emit(event)

        await self.clean_up()
