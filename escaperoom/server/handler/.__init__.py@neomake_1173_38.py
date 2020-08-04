from aiohttp import web
import logging
from ...misc.jsonutils import to_json
from .base import WebHandler


logger = logging.getLogger(__name__)


class MainHandler(WebHandler):

    def __init__(self, rootdir, context):

        from .events import EventsHandler
        from .interface import InterfaceHandler
        from .unit import UnitHandler
        from .gamemaster import GamemasterHandler
        from .etcd import EtcdHandler

        super().__init__(context)

        self.rootdir = rootdir

        self.router.add_get('/', self.get_index)
        self.add_subapp('/events', self.events)

        self.add_subhandler('/interface', InterfaceHandler(self.context))
        self.add_subhandler('/etcd', EtcdHandler(self.context))
        self.add_subhandler('/units', UnitsHandler(self.context))

        self.add_subapp('/units',
                        UnitsHandler(self.events['units'],
                                     context.units_discovery))

    async def get_index(self, request):
        return web.FileResponse(f'{self.rootdir}/index.html')

    async def get_events(self, request):

        from aiohttp_sse import sse_response

        try:
            async with sse_response(request) as resp:
                async for event in self.events:
                    await resp.send(to_json(event))

        except BaseException:
            logger.exception('get /events failed')
