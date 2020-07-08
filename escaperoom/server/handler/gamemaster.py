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

        from datetime import datetime

        gamemasters = {

            0: {
                'id': 0,
                'email': 'emile.zola@read.me',
                'firstname': 'Emile',
                'lastname': 'Zola',
                'creation_date': datetime.now(),
            },

            1: {
                'id': 1,
                'email': 'baubau31@mailchaud.fr',
                'firstname': 'Charles',
                'lastname': 'Baudelaire',
                'creation_date': datetime.now(),
            },

            2: {
                'id': 2,
                'email': 'ocel@realkirikou.org',
                'firstname': 'Michel',
                'lastname': 'Ocelot',
                'creation_date': datetime.now(),
            },

            3: {
                'id': 3,
                'email': 'jean@pasinternet.com',
                'firstname': 'Jean-Baptiste',
                'lastname': 'Poquelin',
                'creation_date': datetime.now(),
            },

        }

        return web.Response(content_type='application/json',
                            text=to_json(gamemasters))
