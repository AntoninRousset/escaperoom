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
        self.events = EventsGenerator()

        self.router.add_get('/', self.get_index)
        self.router.add_get('/favicon.svg', self.get_favicon)
        self.router.add_static('/ressources', f'{self.rootdir}/',
                               append_version=True)

        self.add_subapp('/events', self.events)
        self.add_subapp('/interface/',
                        InterfaceHandler(self.events['interface'],
                                         self.rootdir))
        self.add_subapp('/units/',
                        UnitsHandler(self.events['units'],
                                     context.units_discovery))

    async def get_index(self, request):
        return web.FileResponse(f'{self.rootdir}/monitor.html')

    async def get_favicon(self, request):
        return web.FileResponse(f'{self.rootdir}/icons/favicon.svg')

    async def get_events(self, request):

        from aiohttp_sse import sse_response

        try:
            async with sse_response(request) as resp:
                async for event in self.events:
                    await resp.send(to_json(event))

        except BaseException:
            logger.exception('get /events failed')
