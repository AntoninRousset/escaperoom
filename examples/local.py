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

from escaperoom import *

game = Game('local')

bus = SocketBus('127.0.0.1', 1234, bus_id=0x1, create_server=True)
local = LocalDevice(addr=(bus, 0x1), name='local', type='arduino')
local_state = Attribute(name='state', type=int, value=0)
local.add_attr(local_state)

game.network.add_device(local)

async def play_with_device(attribute):
    import random
    while True:
        await asyncio.sleep(random.randint(3, 7))
        async with attribute.desc_changed:
            attribute.value = random.randint(0, 10000)
            attribute.desc_changed.notify_all()

asyncio.create_task(play_with_device(local_state))

