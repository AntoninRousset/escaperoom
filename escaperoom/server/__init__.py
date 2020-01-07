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
from aiortc import RTCSessionDescription
from os.path import dirname

from . import controls, events_generator, readers

games = dict()
routes = web.RouteTableDef()

@routes.get('/')
async def index(request):
    return web.Response(text=f'available games are {games.keys()}')

@routes.get('/{game_name}')
async def monitor(request):
    game_name = request.match_info['game_name']
    if game_name not in games:
        return ''
    context = {'game_name' : game_name}
    return aiohttp_jinja2.render_template('monitor.jinja2', request, context)

@routes.get('/{game_name}/events')
async def events(request):
    game_name = request.match_info['game_name']
    game = games[game_name]
    async with sse_response(request) as resp:
        async for event in events_generator.generator(game):
            await resp.send(json.dumps(event))
    return resp

@routes.get('/{game_name}/chronometer')
async def chronometer(request):
    game_name = request.match_info['game_name']
    data = await readers.chronometer(games[game_name])
    return web.Response(content_type='application/json', text=json.dumps(data))

@routes.get('/{game_name}/devices')
async def devices(request):
    game_name = request.match_info['game_name']
    data = await readers.devices(games[game_name])
    return web.Response(content_type='application/json', text=json.dumps(data))

@routes.get('/{game_name}/device')
async def device(request):
    game_name = request.match_info['game_name']
    data = await readers.device(games[game_name], request.query['id'])
    return web.Response(content_type='application/json', text=json.dumps(data))

@routes.get('/{game_name}/game')
async def game(request):
    game_name = request.match_info['game_name']
    data = await readers.game(games[game_name])
    return web.Response(content_type='application/json', text=json.dumps(data))

@routes.post('/{game_name}/game')
async def puzzles(request):
    game_name = request.match_info['game_name']
    game = games[game_name]
    params = await request.json()
    answer = await controls.game(game, params)
    return web.Response(content_type='application/json', text=json.dumps(answer))

@routes.get('/{game_name}/puzzles')
async def puzzles(request):
    game_name = request.match_info['game_name']
    data = await readers.puzzles(games[game_name])
    return web.Response(content_type='application/json', text=json.dumps(data))

@routes.get('/{game_name}/puzzle')
async def puzzle(request):
    game_name = request.match_info['game_name']
    game = games[game_name]
    data = await readers.puzzle(games[game_name], request.query['id'])
    return web.Response(content_type='application/json', text=json.dumps(data))

@routes.post('/{game_name}/puzzle')
async def puzzle(request):
    game_name = request.match_info['game_name']
    game = games[game_name]
    params = await request.json()
    answer = await controls.puzzle(game, params, request.query['id'])
    return web.Response(content_type='application/json', text=json.dumps(answer))

@routes.get('/{game_name}/cameras')
async def cameras(request):
    game_name = request.match_info['game_name']
    data = await readers.cameras(games[game_name])
    return web.Response(content_type='application/json', text=json.dumps(data))

@routes.post('/{game_name}/camera')
async def camera(request):
    game_name = request.match_info['game_name']
    game = games[game_name]
    uid = request.query['id']
    camera = game.misc.cameras[uid]
    params = await request.json()
    offer = RTCSessionDescription(sdp=params['sdp'], type=params['type'])
    data = await camera.handle_offer(offer)
    return web.Response(content_type='application/json', text=json.dumps(data))

@routes.post('/{game_name}/display')
async def display(request):
    game_name = request.match_info['game_name']
    game = games[game_name]
    display = game.misc.display
    params = await request.json()
    answer = await display.handle(params) 
    return web.Response(content_type='application/json', text=answer)

app = web.Application()
app.add_routes(routes)
ROOT = dirname(__file__)
#app.router.add_static('/ressources', f'{ROOT}/html/', append_version=True) #TODO
app.router.add_static('/ressources', f'{ROOT}/html/')
aiohttp_jinja2.setup(app, loader=jinja2.FileSystemLoader(f'{ROOT}/html/'))

async def start(host, port):
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, host, port)
    await site.start()
    print(f'Server on {site._host}:{site._port}')

