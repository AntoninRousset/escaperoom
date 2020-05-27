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
import logging

logger = logging.getLogger('escaperoom.server')


async def control(params, service, query=None, server=None):
    try:
        if service == 'action':
            data = await action_control(params, query)
        elif service == 'camera':
            data = await camera_control(params, query)
        elif service == 'device':
            data = await device_control(params, query)
        elif service == 'display':
            data = await cluesdisplay_control(params, query, server)
        elif service == 'game':
            data = await game_control(params, server)
        elif service == 'condition':
            data = await condition_control(params, query)
        else:
            raise RuntimeError('service not found: '+service)
        if data is None:
            return {'state': 'success'}
        return {'state': 'success', 'data': data}
    except Exception as error:
        logger.exception('Failed to execute control')
        return {'state': 'failed', 'reason': str(error)}


async def action_control(params, query):
    action = Action.find_entry(**query)
    if action is None:
        raise RuntimeError('camera not found')
    if params['action'] == 'call':
        action.call()
    elif params['action'] == 'abort':
        await action.abort()
    else:
        raise RuntimeError('action not implemented: '+params['action'])


async def camera_control(params, query):
    camera = Camera.find_entry(**query)
    if camera is None:
        raise RuntimeError('camera not found')
    return await camera.handle_sdp(params['sdp'], params['type'])


async def condition_control(params, query):
    condition = Condition.find_entry(**query)
    if condition is None:
        raise KeyError('condition not found')
    if params['action'] == 'force':
        await condition.force(params['state'])
    elif params['action'] == 'restore':
        await condition.restore()
    elif params['action'] == 'set_state':
        await condition.set_state(params['state'])
    elif params['action'] == 'set_active':
        await condition.set_active(params['state'])
    else:
        raise RuntimeError('action not implemented: '+params['action'])


async def cluesdisplay_control(params, query, server):
    if params['action'] == 'clue':
        if server.give_clue is None:
            raise RuntimeError('giving clue is not implemented by the room')
        await server.give_clue(params['text'])
    else:
        raise RuntimeError('action not implemented: '+params['action'])


async def device_control(params, query):
    device = Device.find_entry(**query)
    if device is None:
        raise KeyError('device not found')
    if params['action'] == 'set_val':
        await device.set_value(params['name'], params['value'])
    elif params['action'] == 'reset':
        await device.reset()
    else:
        raise RuntimeError('action not implemented: '+params['action'])


async def game_control(params, server):
    game = Game.get()
    if game is None:
        raise KeyError('no game defined for the room')
    if params['action'] == 'new_game':
        await game.start()

    elif params['action'] == 'update_options':
        options = params['options']
        # convert planned_date isoformat to datetime.datetime
        if 'planned_date' in options:
            import dateutil.parser
            t = options['planned_date']
            options['planned_date'] = dateutil.parser.parse(t)

        await game.update_options(**options)

    elif params['action'] == 'stop_game':
        await game.stop()
    elif params['action'] == 'buzzer':
        if server.buzzer is None:
            raise RuntimeError('buzzer is not implemented by the room')
        await server.buzzer()
    elif params['action'] == 'end_game':
        print('end_game')
        await game.end()
    else:
        raise RuntimeError('action not implemented: '+params['action'])

