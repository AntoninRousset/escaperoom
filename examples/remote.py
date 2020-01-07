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

game = Game('remote')

bus = SocketBus('127.0.0.1', 1234, bus_id=0x42)
remote = RemoteDevice(name='local')
game.network.add_device(remote)
game.network.add_bus(bus)
