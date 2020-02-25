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

import aiohttp_jinja2, jinja2, json
from aiohttp import web
from aiohttp_sse import sse_response
from os.path import dirname

from . import controls, events_generator, readers

from .. import asyncio, LocalCamera, logging
from ..registered import Registered

ROOT = dirname(__file__)

logger = logging.getLogger('escaperoom.server')

routes = web.RouteTableDef()
interface_routes = web.RouteTableDef()

class Server(Registered):

    _logger = logger


@interface_routes.get('/')
async def monitor(request):
    context = {'game_name' : ''}
    return aiohttp_jinja2.render_template('monitor.jinja2', request, context)

@routes.get('/events')
async def events(request):
    async with sse_response(request) as resp:
        async for event in events_generator.generator():
            await resp.send(json.dumps(event))
    return resp

@routes.get('/{service}')
async def reader(request):
    service = request.match_info['service']
    data = await readers.read(service, request.query)
    return web.Response(content_type='application/json', text=json.dumps(data))

@routes.post('/{service}')
async def control(request):
    service = request.match_info['service']
    answer = await controls.control(await request.json(), service, request.query)
    return web.Response(content_type='application/json', text=json.dumps(answer))


class HTTPServer(Server):

    def __init__(self, host='0.0.0.0', port=8080, *, interface=False):
        super().__init__(name=None)
        self.app = web.Application()
        if interface:
            self._activate_interface()
        self.app.add_routes(routes)
        runner = web.AppRunner(self.app)
        asyncio.run_until_complete(runner.setup())
        self.site = web.TCPSite(runner, host, port)
        self._start(host, port)

    def __str__(self):
        return f'server on {self.site._host}:{self.site._port}'

    def _activate_interface(self):
        self.app.router.add_static('/ressources', f'{ROOT}/html/', append_version=True)
        aiohttp_jinja2.setup(self.app, loader=jinja2.FileSystemLoader(f'{ROOT}/html/'))
        self.app.add_routes(interface_routes)

    def _start(self, host, port):
        asyncio.run_until_complete(self.site.start())
        self._log_info(f'started')

