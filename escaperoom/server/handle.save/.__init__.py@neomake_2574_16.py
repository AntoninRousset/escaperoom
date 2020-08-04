#!/usr/bin/env python
# -*- coding: utf-8 -*-

from aiohttp import web
import logging
from ...misc.jsonutils import to_json

logger = logging.getLogger(__name__)


class MainHandler(web.Application):

    def __init__(self, rootdir, context):

        from .interface import InterfaceHandler
        from .units import UnitsHandler

        super().__init__()
        
        self.rootdir = rootdir

        self.router.add_get('/', self.get_index)
        self.router.add_get('/favicon.svg', self.get_favicon)
        self.router.add_static('/ressources', f'{self.rootdir}/',
                               append_version=True)
        self.router.add_get('/events', self.get_events)

        self.add_subapp('/interface/', InterfaceHandler(self.rootdir))
        self.add_subapp('/units/', UnitsHandler(context.units_discovery))

    async def get_index(self, request):
        return web.FileResponse(f'{self.rootdir}/monitor.html')

    async def get_favicon(self, request):
        return web.FileResponse(f'{self.rootdir}/icons/favicon.svg')

    async def get_events(self, request):
        return web.FileResponse(f'{self.rootdir}/icons/favicon.svg')
