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

from .. import asyncio
from ..misc import Camera, Display
from ..network import Device

async def control(game, params, service, query=None):
    if service == 'camera':
        return await camera_control(game, params, query)
    if service == 'device':
        return await device_control(game, params, query)
    if service == 'display':
        return await display_control(game, params, query)
    if service == 'game':
        return await game_control(game, params)
    if service == 'puzzle':
        return await puzzle_control(game, params, query)

async def camera_control(game, params, query):
    _, camera = Camera.find_camera(**query)
    return await camera.handle_sdp(params['sdp'], params['type'])

async def device_control(game, params, query):
    _, device = Device.find_device(**query)
    if params['action'] == 'set_val':
        try:
            await device.set_value(params['name'], params['value'])
        except (asyncio.TimeoutError, ConnectionError):
            return {'result' : 'failed'}
        finally:
            return {'result' : 'success'}

async def display_control(game, params, query):
    _, display = Display.find_display(**query)
    if params['type'] == 'msg':
        return await display.set_msg(params['msg'])
    elif params['type'] == 'chronometer':
        return await display.set_chronometer(params['running'], params['seconds'])

async def game_control(game, params):
    if params['action'] == 'new_game':
        options = params['options']
        await game.new_game(options)
    elif params['action'] == 'stop_game':
        await game.stop_game()
    return ''

async def puzzle_control(game, params, query):
    _, puzzle = game.logic.find_puzzle(**query)
    if params['action'] == 'activate':
        async with puzzle.desc_changed:
            puzzle.force_active = True
            puzzle.desc_changed.notify_all()
    elif params['action'] == 'complete':
        async with puzzle.desc_changed:
            puzzle.force_completed = True
            puzzle.desc_changed.notify_all()
    elif params['action'] == 'restore':
        async with puzzle.desc_changed:
            puzzle.force_active = False
            puzzle.force_completed = False
            puzzle.desc_changed.notify_all()

