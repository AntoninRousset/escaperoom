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

game = Game('time')

game.network.add_bus(Bus('socket path'))

base_hexa = Device(name='base_hexagon')
b_hexa_state = Attribute(base_hexa, name='state')
base_hexa.add_attr(b_hexa_state)
game.network.add_device(base_hexa)

start = Puzzle('start', initial_state='active')
start.head = lambda: game.start_counter()
start.tail = lambda: print('Bravo')
start.add_condition(b_hexa_state)
start.predicate = lambda: b_hexa_state.value
game.logic.add_puzzle(start, pos=(0,0))

end = Puzzle('end')
end.head = lambda: print('Now remove it to end')
end.tail = lambda: game.stop_counter()
end.add_parent(start)
end.add_condition(b_hexa_state)
end.predicate = lambda: not b_hexa_state.value
game.logic.add_puzzle(end, pos=(0,1))

camera = LocalCamera('video0', '/dev/video0')
game.misc.add_camera(camera)
#camera = LocalCamera('video2', '/dev/video2')
#game.misc.add_camera(camera)

display = Display('http://localhost:8081/')
game.misc.add_display(display)

'''
We could write:
network.add_device(
    Device(name='device')
        .add_attr('state')
        .add_attr('volume')
    )
'''
