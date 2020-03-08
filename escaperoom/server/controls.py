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
from ..game import Game
from ..logic import Action, Condition
from ..misc import Camera, CluesDisplay
from ..network import Device


async def control(params, service, query=None):
    if service == 'camera':
        return await camera_control(params, query)
    if service == 'device':
        return await device_control(params, query)
    if service == 'display':
        return await cluesdisplay_control(params, query)
    if service == 'game':
        return await game_control(params)
    if service == 'condition':
        return await condition_control(params, query)

async def camera_control(params, query):
    camera = Camera.find_entry(**query)
    return await camera.handle_sdp(params['sdp'], params['type'])

async def condition_control(params, query):
    condition = Condition.find_entry(**query)
    if params['action'] == 'activate':
        await condition.force(True)
    elif params['action'] == 'desactivate':
        await condition.force(True)
    elif params['action'] == 'restore':
        await condition.restore()
    elif params['action'] == 'set_true':
        await condition.set_state(True)
    elif params['action'] == 'set_false':
        await condition.set_state(False)

async def cluesdisplay_control(params, query):
    if params['type'] == 'clue':
        print_msg = Action.find_entry('print msg')
        if print_msg is not None:
            print_msg.args = (params['text'], None)
            await print_msg()
        else:
            #name = query['name'] if 'name' in query else '.*'
            name = '.*'
            cluesdisplay = CluesDisplay.find_entry(name=name)
            await cluesdisplay.set_msg(params['text'])

async def device_control(params, query):
    device = Device.find_entry(**query)
    if params['action'] == 'set_val':
        try: await device.set_value(params['name'], params['value'])
        except Exception as e: return {'result' : 'failed'}
        finally: return {'result' : 'success'}
    elif params['action'] == 'reset':
        try: await device.reset()
        except Exception as e: return {'result' : 'failed'}
        finally: return {'result' : 'success'}

async def game_control(params):
    game = Game.find_entry('.*')
    if params['action'] == 'new_game':
        options = params['options']
        async with game.changed:
            await game.start(options)
            game.changed.notify_all()
    elif params['action'] == 'stop_game':
        async with game.changed:
            await game.stop(options)
            game.changed.notify_all()
    return ''

