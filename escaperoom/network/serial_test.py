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

import random, re
from PJON_daemon_client import proto
from math import floor
from copy import deepcopy

from . import asyncio

_packets = asyncio.Queue()

_devices_defaults = {
        1 : {'name' : 'lights_uv',
            'attrs' : {
                0 : {
                    'name' : 'reboot',
                    'type' : 'bool',
                    'value' : '0'
                },
                1 : {
                    'name' : 'state',
                    'type' : 'bool',
                    'value' : '0'
                    }
                }
            },
        2 : {'name' : 'base_cross',
            'attrs' : {
                0 : {
                    'name' : 'reboot',
                    'type' : 'bool',
                    'value' : '0'
                },
                1 : {
                    'name' : 'light_state',
                    'type' : 'bool',
                    'value' : '0'
                    }
                }
            },
        3 : {'name' : 'base_hexagon',
            'attrs' : {
                0 : {
                    'name' : 'reboot',
                    'type' : 'bool',
                    'value' : '0'
                },
                1 : {
                    'name' : 'light_state',
                    'type' : 'bool',
                    'value' : '0'
                    }
                }
            },
        4 : {'name' : 'base_triangle',
            'attrs' : {
                0 : {
                    'name' : 'reboot',
                    'type' : 'bool',
                    'value' : '0'
                },
                1 : {
                    'name' : 'light_state',
                    'type' : 'bool',
                    'value' : '0'
                    }
                }
            },
        5 : {'name' : 'base_star',
            'attrs' : {
                0 : {
                    'name' : 'reboot',
                    'type' : 'bool',
                    'value' : '0'
                },
                1 : {
                    'name' : 'light_state',
                    'type' : 'bool',
                    'value' : '0'
                    }
                }
            }
        }

_devices = deepcopy(_devices_defaults)

COMPUTER_SEND_DELAY = 0
ARDUINO_SEND_DELAY = 0

async def listen():
    while True:
        packet = await _packets.get()
        yield packet
        await asyncio.sleep(0)

async def send(dest, msg):
    delay = random.randint(0, COMPUTER_SEND_DELAY) #TODO Poison distribution
    msg = msg.decode('ascii')[:-1]
    await asyncio.sleep(delay)
    if dest == 0:
        for device_id in _devices:
            asyncio.create_task(_device_answer(device_id, msg))
    else:
        asyncio.create_task(_device_answer(dest, msg))
    return proto.OutgoingResult.SUCCESS

async def _device_answer(dest, msg):
    device = _devices[dest]
    attrs = device['attrs']
    if re.match('\s*get\s+desc\s*', msg):
        name = device['name']
        n_attrs = len(attrs)
        return await _new_packet(dest, f'desc {name} {n_attrs}')
    if re.match('\s*get\s+attr\s+\d+\s*', msg):
        attr_id = int(msg.split()[2])
        attr = attrs[attr_id]
        name, type = attr['name'], attr['type']
        return await _new_packet(dest, f'attr {attr_id} {name} {type}')
    if re.match('\s*get\s+val\s+\d+\s*', msg):
        attr_id = int(msg.split()[2])
        attr = attrs[attr_id]
        return await _new_packet(dest, f'val {attr_id} {attr["value"]}') 
    if re.match('\s*set\s+val\s+\d+\s+\w+\s*', msg):
        attr_id = int(msg.split()[2])
        attr = attrs[attr_id]
        attr['value'] = msg.split()[3]
        if attr['name'] == 'reboot' and float(attr['value']):
            for id in _devices_defaults.keys():
                _devices[id] = deepcopy(_devices_defaults[id])
        return await _new_packet(dest, f'val {attr_id} {attr["value"]}') 

async def _new_packet(src, msg, *, random_wait=True):
    async def wait_and_pack(delay):
        await asyncio.sleep(delay)
        data = (msg+'\0').encode('ascii')
        await _packets.put(proto.PacketIngoingMessage(src, data))
    delay = random.randint(0, ARDUINO_SEND_DELAY) #TODO Poison distribution
    return await wait_and_pack(delay)

async def _events_creator():
    while True:
        await asyncio.sleep(2)
        await _new_packet(2, f'val 0 {random.randint(0, 100)}')

#asyncio.create_task(_events_creator())

'''
Remarks:
- We should avoid for an arduino to ping_back twice at once, i.e. when it has
  received a second ping from the computer while he was trying to answer to the
  first one. This could be generalised to any question-like packet from the
  computer, although it may need some work on the arduino's side...
'''
