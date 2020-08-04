#!/usr/bin/env python
# -*- coding: utf-8 -*-

from asyncio import Lock


class EventSource:

    def __init__(self):
        self.lock = Lock()
        self.subscriptions = set()

    async def subscribe(self):

        print('SUBSCRIBE', flush=True)

        from .subscription import Subscription
        from weakref import ref

        sub = Subscription(self)

        async with self.lock:
            self.subscriptions.add(ref(sub))

        print('--->', sub, flush=True)
        return sub

    async def clean_up(self):

        async with self.lock:
            self.subscriptions = {ref for ref in self.subscriptions
                                  if ref() is not None}

    async def emit(self, event):

        for sub_ref in self.subcriptions:

            sub = sub_ref()

            if sub is not None:
                await sub.emit(event)

        await self.clean_up()
