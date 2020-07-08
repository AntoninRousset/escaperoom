#!/usr/bin/env python
# -*- coding: utf-8 -*-

from aiohttp import web
import logging
from . import to_json

logger = logging.getLogger(__name__)


class UnitsHandler(web.Application):

    def __init__(self, events, units_discovery):

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

        self.events.add_source(periodic_event())

    def get_all_units(self, request):

        def rstr():
            from string import ascii_lowercase
            from random import randint, choices
            k = randint(4, 12)
            return ''.join(choices(ascii_lowercase, k=k))

        def create_random_unit():
            from random import randint, choice
            field = {'name', 'hostname', 'ipaddr', 'port', 'active',
                     'registered'}
            field = {f: rstr() for f in field}
            field['active'] = choice({False, True})
            field['enabled'] = choice({False, True})

        from random import randint, choices
        n = 5
        units = {k: create_random_unit()
                 for k in choices(range(n), k=randint(1, n))}

        return web.Response(content_type='application/json',
                            text=to_json(units))
