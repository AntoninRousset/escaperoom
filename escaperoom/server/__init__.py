'''
 This program is free software: you can redistribute it and/or modify
 it under the terms of the GNU General Public License as published by
 the Free Software Foundation, version 3.
 This program is distributed in the hope that it will be useful, but
 WITHOUT ANY WARRANTY; without even the implied warranty of
 MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
 General Public License for more details.
 You should have received a copy of the GNU General Public License
 along with this program. If not, see <http://www.gnu.org/licenses/>.
'''

from aiohttp import web
from aiohttp_sse import sse_response
from os.path import dirname

from . import controls, events_generator, readers
from .json_utils import to_json

from .. import asyncio, logging
from ..registered import Registered

ROOT = dirname(__file__)

logger = logging.getLogger('escaperoom.server')

routes = web.RouteTableDef()
interface_routes = web.RouteTableDef()


class Server(Registered):

    _logger = logger


@interface_routes.get('/')
async def monitor(request):
    try:
        return web.FileResponse(f'{ROOT}/html/monitor.html')
    except BaseException:
        logger.exception('GET "/" failed')


@routes.get('/favicon.svg')
async def favicon(request):
    try:
        return web.FileResponse(f'{ROOT}/html/icons/favicon.svg')
    except BaseException:
        logger.exception('GET "/favicon.svg" failed')


@routes.get('/events')
async def events(request):
    try:
        async with sse_response(request) as resp:
            async for event in events_generator.generator():
                await resp.send(to_json(event))
        return resp
    except BaseException:
        logger.exception('GET "/events" failed')


@routes.get('/{service}')
async def reader(request):
    service = request.match_info['service']
    try:
        data = await readers.read(service, request.query, request.app)
        return web.Response(content_type='application/json',
                            text=to_json(data))
    except BaseException:
        logger.exception(f'GET "{service}" failed')


@routes.post('/{service}')
async def control(request):
    service = request.match_info['service']
    try:
        ans = await controls.control(await request.json(), service,
                                     request.query, server=request.app)
        return web.Response(content_type='application/json', text=to_json(ans))
    except BaseException:
        logger.exception(f'POST "{service}" failed')


class HTTPServer(Server, web.Application):

    def __init__(self, host='0.0.0.0', port=8080, *, interface=False,
                 main_chronometer=None, give_clue=None, buzzer=None):
        Server.__init__(self, name=None)
        web.Application.__init__(self)
        if interface:
            self._activate_interface()
        self.add_routes(routes)
        runner = web.AppRunner(self, logger=self._logger)
        asyncio.run_until_complete(runner.setup())
        self.site = web.TCPSite(runner, host, port)
        self._start(host, port)
        self.main_chronometer = main_chronometer
        self.give_clue = give_clue
        self.buzzer = buzzer

    def __str__(self):
        return f'server on {self.site._host}:{self.site._port}'

    def _activate_interface(self):
        self.router.add_static('/ressources', f'{ROOT}/html/',
                               append_version=True)
        self.add_routes(interface_routes)

    def _start(self, host, port):
        asyncio.run_until_complete(self.site.start())
        self._log_info(f'started')
