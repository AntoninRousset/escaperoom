#!/usr/bin/env python
# -*- coding: utf-8 -*-

from aiohttp import web
import logging
from . import to_json
from ...event import Event, EventSource, EventSink


logger = logging.getLogger(__name__)


class UnitHandler(web.Application, ):

    def __init__(self, web_event_source, units_discovery):

        super().__init__()

        self.units_discovery = units_discovery
        self.router.add_get('', self.get_all_units)

        self.events = events

        async def periodic_event():

            from asyncio import sleep

            while True:
                print('--- sending ---')
                yield 'salut'
                await sleep(5)

        self.events.add_event_source(periodic_event())

    def get_all_units(self, request):

        def rstr():
            from string import ascii_lowercase
            from random import randint, choices
            k = randint(4, 12)
            return ''.join(choices(ascii_lowercase, k=k))

        def create_random_unit():
            from random import choice
            field = {'name', 'hostname', 'ipaddr', 'port'}
            unit = {f: rstr() for f in field}
            unit['active'] = choice([False, True])
            unit['registered'] = choice([False, True])
            return unit

        from random import randint, choices
        n = 5
        units = {k: create_random_unit()
                 for k in choices(range(n), k=randint(1, n))}

        return web.Response(content_type='application/json',
                            text=to_json(units))
