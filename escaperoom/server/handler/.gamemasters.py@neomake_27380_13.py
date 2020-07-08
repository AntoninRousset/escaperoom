#!/usr/bin/env python
# -*- coding: utf-8 -*-

from aiohttp import web
import logging
from . import to_json

logger = logging.getLogger(__name__)


class GamemastersHandler(web.Application):

    def __init__(self, events):

        super().__init__()

        self.router.add_get('', self.get_all_gamemasters)
        self.events = events

    def get_all_gamemasters(self, request):

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
