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
from ..network.devices import Device

_packets = asyncio.Queue()

_devices_defaults = {
        1 : {
            'name' : 'lights',
            'attrs' : {
                0 : {
                    'name' : 'room1',
                    'type' : 'bool',
                    'value' : '1'
                    },
                1 : {
                    'name' : 'room2',
                    'type' : 'bool',
                    'value' : '1'
                    },
                2 : {
                    'name' : 'vessel',
                    'type' : 'bool',
                    'value' : '1'
                    },
                3 : {
                    'name' : 'uv',
                    'type' : 'bool',
                    'value' : '0'
                    }
                }
            },
        2 : {
            'name' : 'base_cross',
            'attrs' : {
                0 : {
                    'name' : 'hall',
                    'type' : 'bool',
                    'value' : '0'
                    },
                1 : {
                    'name' : 'light',
                    'type' : 'bool',
                    'value' : '0'
                    }
                }
            },
        3 : {
            'name' : 'base_hexagon',
            'attrs' : {
                0 : {
                    'name' : 'hall',
                    'type' : 'bool',
                    'value' : '0'
                    },
                1 : {
                    'name' : 'light',
                    'type' : 'bool',
                    'value' : '0'
                    }
                }
            },
        4 : {
            'name' : 'base_triangle',
            'attrs' : {
                0 : {
                    'name' : 'hall',
                    'type' : 'bool',
                    'value' : '0'
                    },
                1 : {
                    'name' : 'light',
                    'type' : 'bool',
                    'value' : '0'
                    },
                2 : {
                    'name' : 'fuse',
                    'type' : 'bool',
                    'value' : '1'
                    },
                3 : {
                    'name' : 'led',
                    'type' : 'bool',
                    'value' : '0'
                    }
                }
            },
        5 : {
            'name' : 'base_star',
            'attrs' : {
                0 : {
                    'name' : 'hall',
                    'type' : 'bool',
                    'value' : '0'
                    },
                1 : {
                    'name' : 'light',
                    'type' : 'bool',
                    'value' : '0'
                    }
                }
            },
        6 : {
            'name' : 'box_connect',
            'attrs' : {
                0 : {
                    'name' : 'fuse0',
                    'type' : 'bool',
                    'value' : '1'
                    },
                1 : {
                    'name' : 'fuse1',
                    'type' : 'bool',
                    'value' : '1'
                    },
                2 : {
                    'name' : 'fuse2',
                    'type' : 'bool',
                    'value' : '0'
                    },
                3 : {
                    'name' : 'led0',
                    'type' : 'bool',
                    'value' : '0'
                    },
                4 : {
                    'name' : 'led1',
                    'type' : 'bool',
                    'value' : '0'
                    },
                5 : {
                    'name' : 'led2',
                    'type' : 'bool',
                    'value' : '0'
                    },
                6 : {
                    'name' : 'jacks',
                    'type' : 'bool',
                    'value' : '0'
                    }
                }
            },
        7 : {
            'name' : 'box_code',
            'attrs' : {
                0 : {
                    'name' : 'state',
                    'type' : 'bool',
                    'value' : '0'
                    },
                1 : {
                    'name' : 'target',
                    'type' : 'int',
                    'value' : 1234
                    },
                2 : {
                    'name' : 'red',
                    'type' : 'bool',
                    'value' : '0'
                    },
                3 : {
                    'name' : 'green',
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
        try:
            packet = _packets.get_nowait()
        except asyncio.QueueEmpty:
            packet = await _packets.get()
        yield packet
        await asyncio.sleep(0)

async def send(dest, msg):
    delay = random.randint(0, COMPUTER_SEND_DELAY) #TODO Poison distribution
    delay = COMPUTER_SEND_DELAY
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
        name, type, val = attr['name'], attr['type'], attr['value']
        return await _new_packet(dest, f'attr {attr_id} {name} {type} {val}')
    if re.match('\s*get\s+val\s+\d+\s*', msg):
        attr_id = int(msg.split()[2])
        attr = attrs[attr_id]
        return await _new_packet(dest, f'val {attr_id} {attr["value"]}') 
    if re.match('\s*set\s+val\s+\d+\s+\w+\s*', msg):
        attr_id = int(msg.split()[2])
        attr = attrs[attr_id]
        attr['value'] = msg.split()[3]
        return await _new_packet(dest, f'val {attr_id} {attr["value"]}') 
    if re.match('\s*reboot\s*', msg):
        for id in _devices_defaults.keys():
            _devices[id] = deepcopy(_devices_defaults[id])
        return

async def _new_packet(src, msg, *, random_wait=True):
    async def wait_and_pack(delay):
        await asyncio.sleep(delay)
        data = (msg+'\0').encode('ascii')
        await _packets.put(proto.PacketIngoingMessage(src, data))
    delay = random.randint(0, ARDUINO_SEND_DELAY) #TODO Poison distribution
    return await wait_and_pack(delay)

async def _events_creator():
    from .. import Game
    while True:
        game = Game.find_entry('.*')
        if game is not None:
            break
        await Game.group_changed().wait()
    while True:
        vessel = Device.find_entry('vessel')
        if vessel is not None:
            break
        await Device.group_changed().wait()
    while not game:
        async with game.changed:
            await game.changed.wait()

    print('* starting events *')
    await asyncio.sleep(57)

    print('* ignition *')
    await vessel.set_value('ignition', True)
    await asyncio.sleep(0.5)

    print('* unignition *')
    await vessel.set_value('ignition', False)
    await asyncio.sleep(1)

    print('* ignition *')
    await vessel.set_value('ignition', True)
    await asyncio.sleep(4)

    print('* start *')
    await vessel.set_value('start', True)
    await asyncio.sleep(0.1)
    await vessel.set_value('start', False)
    await asyncio.sleep(70)

    print('* Remove fuse 1 *')
    _devices[6]['attrs'][0]['value'] = '0'
    await _new_packet(6, 'val 0 1')
    await asyncio.sleep(2)

    print('* Put fuse 3 *')
    _devices[6]['attrs'][2]['value'] = '1'
    await _new_packet(6, 'val 2 1')
    await asyncio.sleep(4)

    print('* Put fuse 1 *')
    _devices[6]['attrs'][0]['value'] = '1'
    await _new_packet(6, 'val 0 1')
    await asyncio.sleep(2)

    print('* Jacks connected *')
    _devices[6]['attrs'][6]['value'] = '1'
    await _new_packet(6, 'val 6 1')
    await asyncio.sleep(2)

    print('* Date entered *')
    _devices[7]['attrs'][0]['value'] = '1'
    await _new_packet(7, 'val 0 1')
    await asyncio.sleep(5)

    print('* reignition *')
    await vessel.set_value('ignition', False)
    await asyncio.sleep(0.1) #TODO
    await vessel.set_value('ignition', True)
    await asyncio.sleep(20)

    print('* Date changed *')
    _devices[7]['attrs'][0]['value'] = '0'
    await _new_packet(7, 'val 0 0')
    await asyncio.sleep(4)

    print('* Date entered *')
    _devices[7]['attrs'][0]['value'] = '1'
    await _new_packet(7, 'val 0 1')
    await asyncio.sleep(2)

    print('* reignition *')
    await vessel.set_value('ignition', False)
    await asyncio.sleep(0.1) #TODO
    await vessel.set_value('ignition', True)
    await asyncio.sleep(5)

    print('* start *')
    await vessel.set_value('start', True)
    await asyncio.sleep(0.1) #TODO, or it misses it
    await vessel.set_value('start', False)
    await asyncio.sleep(30)


    for i in range(2, 5):
        print(f'* base {i} *')
        _devices[i]['attrs'][0]['value'] = '1'
        await _new_packet(i, 'val 0 1')
    await asyncio.sleep(5)
    print(f'* unbase {4} *')
    _devices[4]['attrs'][0]['value'] = '0'
    await _new_packet(4, 'val 0 0')
    for i in range(4, 6):
        print(f'* base {i} *')
        _devices[i]['attrs'][0]['value'] = '1'
        await _new_packet(i, 'val 0 1')

asyncio.create_task(_events_creator())

