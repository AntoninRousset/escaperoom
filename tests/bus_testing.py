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

import asyncio, random
from math import floor

packets = asyncio.Queue()

n_device = lambda : 3
n_comp = lambda : random.randint(1, 2)
n_attr = lambda : random.randint(1, 4)

names = {'Phil', 'Shade', 'Karly', 'Emelia', 'Mauricio', 'Leona', 'Kensey', 'Walt', 'Marina', 'Don', 'Tai', 'Stan', 'Adrianna', 'Coral', 'Tyra', 'Ezio', 'Isis', 'Nichole', 'Caoimhe', 'Adam', 'Mikey', 'Freddy', 'Angelina', 'Electra', 'Dee', 'May', 'Priya', 'Jordan', 'Arwen', 'Elin', 'Stacia', 'Arman', 'Dominique', 'Rupert', 'Mike', 'Monica', 'Zia', 'Chayton'}
_n_device = n_device()
devices = dict()
for device_id, device_name in zip(range(1, _n_device+1), random.sample(names, _n_device)): 
    _n_comp = n_comp() 
    comps = list()
    for comp_name in random.sample(names, _n_comp): 
        _n_attr = n_attr()
        attrs = list()
        for attr_name in random.sample(names, _n_attr):
            attrs.append({'name' : attr_name, 'type' : 'float', 'value' : '0'})
        comps.append({'name' : comp_name, 'attrs' : attrs})
    devices[device_id] = {'name' : device_name, 'comps' : comps} 

COMPUTER_SEND_DELAY = 0
ARDUINO_SEND_DELAY = 0

# The computer listen
async def listen():
    asyncio.get_event_loop().create_task(events_creator())
    while True:
        await asyncio.sleep(0)
        packet = await packets.get()
        yield packet

# The computer send
async def send(dest, msg):
    delay = random.randint(0, COMPUTER_SEND_DELAY) #TODO Poison distribution
    await asyncio.sleep(delay)
    if dest == 0:
        for device_id in devices:
            asyncio.get_event_loop().create_task(device_answer(device_id, msg))
    else:
        asyncio.get_event_loop().create_task(device_answer(dest, msg))
    return True

# Emulate device's answers 
async def device_answer(dest, msg):
    import re
    if msg == 'ping':
        return new_packet(dest, 'ping_back')
    device = devices[dest]
    if msg == 'get name':
        return new_packet(dest, f'upt name {device["name"]}')
    comps = device["comps"]
    if msg == 'get n_comp':
        return new_packet(dest, f'upt n_comp {len(comps)}')
    comp_id = int(msg.split()[2])
    comp = comps[comp_id]
    if re.match('get comp \d+ name', msg):
        return new_packet(dest, f'upt comp {comp_id} name {comp["name"]}')
    attrs = comp["attrs"]
    if re.match('get comp \d+ n_attr', msg):
        return new_packet(dest, f'upt comp {comp_id} n_attr {len(comp["attrs"])}')
    attr_id = int(msg.split()[4])
    attr = attrs[attr_id]
    if re.match('get comp \d+ attr \d+ desc', msg):
        return new_packet(dest, f'upt comp {comp_id} attr {attr_id} desc {attr["name"]} {attr["type"]}')
    if re.match('get comp \d+ attr \d+ value', msg):
        return new_packet(dest, f'upt comp {comp_id} attr {attr_id} value {attr["value"]}')

# Create a packet sent by a device
def new_packet(src, msg, wait=False, *, random_wait=True):
    async def wait_and_pack(delay):
        await asyncio.sleep(delay)
        await packets.put((src, msg))
    delay = random.randint(0, ARDUINO_SEND_DELAY) #TODO Poison distribution
    if wait:
        return wait_and_pack(delay)
    else:
        asyncio.get_event_loop().create_task(wait_and_pack(delay))

# Random events
async def events_creator():
    while True:
        await asyncio.sleep(10)
        #new_packet(34, 'hello!')

'''
Remarks:
- We should avoid for an arduino to ping_back twice at once, i.e. when it has
  received a second ping from the computer while he was trying to answer to the
  first one. This could be generalised to any question-like packet from the
  computer, although it may need some work on the arduino's side...
'''
