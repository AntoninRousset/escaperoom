#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
from . import to_json
from .base import WebHandler


LOGGER = logging.getLogger(__name__)


class GamemastersHandler(WebHandler):

    def __init__(self, context, rootdir):

        super().__init__(context, rootdir)
        self.app.router.add_get('', self.get_all_gamemasters)

    def get_all_gamemasters(self, request):

        from aiohttp.web import Response

        return Response(content_type='application/json',
                        text=to_json(['a', 'b', 'c']))
