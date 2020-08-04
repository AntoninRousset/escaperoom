#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
from . import to_json
from .base import WebHandler


logger = logging.getLogger(__name__)


class UnitHandler(WebHandler):

    def __init__(self, context):

        super().__init__(context)

        self.app.router.add_get('', self.get_all_units)

    def get_all_units(self, request):

        from aiohttp.web import Response

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

        return Response(content_type='application/json',
                        text=to_json(units))
