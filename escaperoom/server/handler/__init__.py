from aiohttp import web
import logging
from .base import WebHandler
from ...misc.jsonutils import to_json

LOGGER = logging.getLogger(__name__)


class MainHandler(WebHandler):

    def __init__(self, context, rootdir):

        from .interface import InterfaceHandler
        from .units import UnitsHandler
        from .gamemasters import GamemastersHandler
        from .etcd import EtcdHandler

        super().__init__(context, rootdir)

        self.app.router.add_get('/', self.get_index)
        self.app.router.add_get('/events', self.get_events)

        args = (self.context, self.rootdir)
        self.add_subhandler('/interface', InterfaceHandler(*args))
        self.add_subhandler('/etcd', EtcdHandler(*args))
        self.add_subhandler('/units', UnitsHandler(*args))
        self.add_subhandler('/gamemasters', GamemastersHandler(*args))

    async def get_index(self, request):
        return web.FileResponse(f'{self.rootdir}/index.html')

    async def get_events(self, request):

        from asyncio import CancelledError
        from aiohttp_sse import sse_response

        try:
            print('## new sse ##')
            async with sse_response(request) as resp:
                async with self.subscribe() as sub:
                    async for event in sub:
                        print('-- event', event)
                        await resp.send(to_json(event))

        except CancelledError:
            print('## stop sse ##')

        except BaseException:
            LOGGER.exception('get /events failed')
