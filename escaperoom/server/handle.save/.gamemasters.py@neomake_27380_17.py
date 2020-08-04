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

        gamemasters = {
            ''
        }

        return web.Response(content_type='application/json',
                            text=to_json(gamemasters))
