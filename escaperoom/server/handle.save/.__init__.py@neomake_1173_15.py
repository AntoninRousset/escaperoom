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

        interface = InterfaceHandler(self.context)
        self.app.add_subapp('/interface', interface.app)
        self.app.add_event_source(interface)



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
