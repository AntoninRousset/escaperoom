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

from .. import asyncio, logging
from ..game import Game
from ..node import Node

ROOT = dirname(__file__)

logger = logging.getLogger('escaperoom.server')

routes = web.RouteTableDef()
interface_routes = web.RouteTableDef()

class Server(Node):

    _logger = logger

@interface_routes.get('/')
async def index(request):
    games_names = {game.name for game in Game.nodes()}
    return web.Response(text=f'available games are {games_names}')

@interface_routes.get('/{game_name}')
async def monitor(request):
    game_name = request.match_info['game_name']
    if game_name not in {game.name for game in Game.nodes()}:
        return ''
    context = {'game_name' : game_name}
    return aiohttp_jinja2.render_template('monitor.jinja2', request, context)

@routes.get('/{game_name}/events')
async def events(request):
    game = Game.find_node(name=request.match_info['game_name'])
    async with sse_response(request) as resp:
        async for event in events_generator.generator(game):
            await resp.send(json.dumps(event))
    return resp

@routes.get('/{game_name}/{service}')
async def reader(request):
    game = Game.find_node(name=request.match_info['game_name'])
    service = request.match_info['service']
    data = await readers.read(game, service, request.query)
    return web.Response(content_type='application/json', text=json.dumps(data))

@routes.post('/{game_name}/{service}')
async def puzzles(request):
    game = Game.find_node(name=request.match_info['game_name'])
    service = request.match_info['service']
    answer = await controls.control(game, await request.json(), service, request.query)
    return web.Response(content_type='application/json', text=json.dumps(answer))

class HTTPServer(Server):

    _group = dict()

    #TODO can we use port 80?
    def __init__(self, host='0.0.0.0', port=8080, *, interface=False):
        super().__init__(name=None)
        self.app = web.Application()
        if interface:
            self._activate_interface()
        self.app.add_routes(routes)
        self._start(host, port)

    def _activate_interface(self):
        self.app.router.add_static('/ressources', f'{ROOT}/html/', append_version=True)
        aiohttp_jinja2.setup(self.app, loader=jinja2.FileSystemLoader(f'{ROOT}/html/'))
        self.app.add_routes(interface_routes)

    def _start(self, host, port):
        runner = web.AppRunner(self.app)
        asyncio.run_until_complete(runner.setup())
        site = web.TCPSite(runner, host, port)
        asyncio.run_until_complete(site.start())
        self._log_info(f'server on {site._host}:{site._port}')

