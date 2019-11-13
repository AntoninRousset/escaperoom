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


name = 'time'

network = Network()
network.add_bus(Bus('socket path'))

base_hexa = Device(name='base_hexagon')
b_hexa_state = Attribute(base_hexa, name='state')
base_hexa.add_attr(b_hexa_state)
network.add_device(base_hexa)

logic = Logic()

start = Puzzle('start', state='active')
start.head = lambda: print('Place the pod to start')
start.tail = lambda: print('Bravo')
start.add_condition(b_hexa_state)
start.predicate = lambda: b_hexa_state.value
logic.add_puzzle(start, pos=(0,0))

end = Puzzle('end')
end.head = lambda: print('Now remove it to end')
end.tail = lambda: print('You win')
end.add_parent(start)
end.add_condition(b_hexa_state)
end.predicate = lambda: not b_hexa_state.value
logic.add_puzzle(end, pos=(0,1))

misc = Misc()

main_camera = LocalCamera('video0', '/dev/video0')
misc.add_camera(main_camera)
#other_camera = LocalCamera('video2', '/dev/video2')
#misc.add_camera(other_camera)

'''
# start 
node = game.add(name='start', Node(reversible=False))
node.head = lambda self: print('mouahaha')
node.add_conditions(Event(device=3, component='door', to='off')

# launch
# give a lambda as a condition for Events
game.add(Event(name='switch 1', device=1, component='switch1', to='on'))
game.add(Event(name='switch 2', device=1, component='switch2', to='on'))
game.add(Event(name='switch 2', device=1, component='switch3', to='on'))
## Shared node telling there is enough power 
node = game.add(Node(name='enough power'))
node.add_parents(*game.gets('start'))
node.add_conditions(*game.gets('switch 1', 'switch 2', 'switch 3'))
## Shared story element for the launching
node = game.add(Node(name='launch', reversible=False))
node.add_parents('start')
node.add_conditions(Event(device=2, component='pushbutton', to='on'))
## Anonymous node - contained in the story element - corresponding to the monitor
node = node.add(Node(reversible=False))
node.add_parents(*game.gets('enough power'))
node.add_conditions('launch button')
node.head = lambda self: print('ready for launch (wip: turn on a light)')
node.tail = lambda self: print('launching!!')

# end
game.add(Event(name='door opened', device=3, component='door', to='on', fr='off'))

node = game.add(Node(name='end', reversible=False))
node.add_parents('launch')
node.add_conditions(*game.gets('door opened'))

game.add_conditions(node)
'''
