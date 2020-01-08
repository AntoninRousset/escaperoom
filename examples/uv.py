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

import asyncio

from escaperoom import *

# Features:
# - Translate a physical events into a node
# - Anonymous (non-retrievable) nodes
# - AND operation throught conditions
# - OR operation throught parents
# - Easy access to non-anonymous nodes
# - Custom head and tail with lambda
# - Ability to redefine Game, Node and Event
# - Concise writing
# - No restriction of order

game = Game('uv')

game.network.add_bus(SerialBus('socket path'))

base_hexa = RemoteDevice(name='base_hexagon')
bh_state = Attribute(name='hall_state')
base_hexa.add_attr(bh_state)
game.network.add_device(base_hexa)

lights_uv = RemoteDevice(name='lights_uv')
lu_state = Attribute(name='uv_state')
lights_uv.add_attr(lu_state)
game.network.add_device(lights_uv)

async def monitor_state():
    while True:
        async with bh_state.desc_changed:
            await bh_state.desc_changed.wait()
            if bh_state.value == True:
                await lights_uv.send(f'set val {lu_state.attr_id} 1')
asyncio.create_task(monitor_state())
