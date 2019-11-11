#!/usr/bin/env python

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
import aiohttp_jinja2, jinja2
import asyncio
import json

import settings
#settings.testing = 'b3'

import asyncio, sys

def read_devices(game):
    descs = dict()
    for uid, device in game.network.devices.items():
        descs[uid] = {'name' : device.name, 'n_attr' : device.n_attr}
    descs_changed = game.network.devices_changed
    return descs, descs_changed 

def read_device(device):
    attrs = {uid : {'name' : attr.name, 'type' : attr.vtype, 'value' : attr.value}
            for uid, attr in device.attrs.items()}
    info = {'name' : device.name, 'attrs' : attrs,
            'addr' : device.addr, 'msg' : device.msg}
    return info

def read_puzzles(game):
    descs = dict()
    for uid, puzzle in game.logic.puzzles.items():
        col, row = game.logic.positions[uid]
        descs[uid] = {'name' : puzzle.name, 'state' : puzzle.state,
                      'row' : row, 'col' : col} 
    descs_changed = game.logic.puzzles_changed
    return descs, descs_changed 

def read_puzzle(game, uid):
    puzzle = game.logic.puzzles[uid]
    info = {'uid' : uid, 'name' : puzzle.name}
    info_changed = puzzle.puzzle_changed
    return info, info_changed 

def read_cameras(game):
    descs = dict()
    for uid, camera in game.misc.cameras.items():
        descs[uid] = {'name' : camera.name}
    descs_changed = game.misc.cameras_changed
    return descs, descs_changed

games = dict()
routes = web.RouteTableDef()

@routes.get('/')
async def index(request):
    return web.Response(text=f'available games are {games.keys()}')

@routes.get('/{game_name}')
async def monitor(request):
    game_name = request.match_info['game_name']
    context = {'game_name' : game_name}
    return aiohttp_jinja2.render_template('./html/monitor.jinja2', request, context)

@routes.get('/{game_name}/receiver')
async def sender(request):
    game_name = request.match_info['game_name']
    context = {'game_name' : game_name}
    return aiohttp_jinja2.render_template('./html/receiver.jinja2', request, context)

@routes.get('/{game_name}/streamer')
async def sender(request):
    game_name = request.match_info['game_name']
    context = {'game_name' : game_name}
    return aiohttp_jinja2.render_template('./html/streamer.jinja2', request, context)

@routes.get('/{game_name}/{script_name}.js')
async def script(request):
    script_name = request.match_info['script_name']
    content = open(f'./html/{script_name}.js', 'r').read()
    return web.Response(content_type='application/javascript', text=content)

@routes.get('/{game_name}/{style_name}.css')
async def style(request):
    style_name = request.match_info['style_name']
    content = open(f'./html/{style_name}.css', 'r').read()
    return web.Response(content_type='text/css', text=content)

@routes.get('/{game_name}/{style}.css')
async def monitor(request):
    game_name = request.match_info['game_name']
    context = {'game_name' : game_name}
    return aiohttp_jinja2.render_template('./html/monitor.jinja2', request, context)

@routes.get('/{game_name}/devices')
async def devices(request):
    game_name = request.match_info['game_name']
    game = games[game_name]
    async with sse_response(request) as resp:
        while True:
            devices, devices_changed = read_devices(game) 
            async with devices_changed:
                await resp.send(json.dumps(devices))
                await devices_changed.wait()
    return resp

@routes.get('/{game_name}/device')
async def device(request):
    game_name = request.match_info['game_name']
    game = games[game_name]
    uid = request.query['id']
    device = game.network.devices[uid]
    async with sse_response(request) as resp:
        while True:
            data = read_device(device) 
            await resp.send(json.dumps(data))
            await device.changed.wait()
    return resp

@routes.get('/{game_name}/puzzles')
async def puzzles(request):
    game_name = request.match_info['game_name']
    game = games[game_name]
    async with sse_response(request) as resp:
        while True:
            puzzles, puzzles_changed = read_puzzles(game) 
            async with puzzles_changed:
                await resp.send(json.dumps(puzzles))
                await puzzles_changed.wait()
    return resp

@routes.get('/{game_name}/puzzle')
async def puzzle(request):
    game_name = request.match_info['game_name']
    game = games[game_name]

@routes.get('/{game_name}/cameras')
async def cameras(request):
    game_name = request.match_info['game_name']
    game = games[game_name]
    async with sse_response(request) as resp:
        while True:
            cameras, cameras_changed = read_cameras(game)
            async with cameras_changed:
                await resp.send(json.dumps(cameras))
                await cameras_changed.wait()
    return resp

from aiortc import RTCSessionDescription
@routes.post('/{game_name}/camera')
async def camera(request):
    game_name = request.match_info['game_name']
    game = games[game_name]
    uid = request.query['id']
    camera = game.misc.cameras[uid]

    params = await request.json()
    offer = RTCSessionDescription(sdp=params['sdp'], type=params['type'])
    answer = await camera.handle_offer(offer)
    return web.Response(content_type='application/json', text=json.dumps(answer))

async def main():
    #from games import b3
    #games['b3'] = b3

    from games import time
    games['time'] = time

    await start_server()
    while True:
        await asyncio.sleep(3600)


async def start_server():
    app = web.Application()
    aiohttp_jinja2.setup(app, loader=jinja2.FileSystemLoader('./'))
    app.add_routes(routes)

    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, 'localhost', 8080)

    await site.start()
    print(f'Running on {site._host}:{site._port}')
    while True:
        await asyncio.sleep(3600)
    await runner.cleanup()
 
import signal

def shutdown(loop, signal=None):
    if signal:
        print('shutdown signal')

def custom_exception_handler(loop, context):
    loop.default_exception_handler(context)
    exception = context.get('exception')
    print(context)

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    #for s in (signal.SIGHUP, signal.SIGTERM, signal.SIGINT):
    #    loop.add_signal_handler(s, shutdown(loop, signal=s))
    loop.set_exception_handler(custom_exception_handler)
    loop.create_task(main())
    loop.run_forever()

