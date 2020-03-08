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
from ..network import Device
from ..misc import Chronometer

class SharedQueue(asyncio.Queue, asyncio.Condition):
    def __init__(self):
        asyncio.Queue.__init__(self)
        asyncio.Condition.__init__(self)

    async def get(self):
        async with self:
            await self.wait()
            return await super().get()

    async def put(self, item):
        async with self:
            await super().put(item)
            super().notify_all()

events_queues = dict()

async def generator():
    events_queue = SharedQueue()
    categories = {game_events, actions_events,
                  conditions_events, devices_events}
    for events in categories:
        asyncio.create_task(events(events_queue))
    while True:
        try:
            event = events_queue.get_nowait()
        except asyncio.QueueEmpty:
            event = await events_queue.get()
        yield event

async def game_events(events_queue):
    game = Game.find_entry('.*')
    while True:
        async with game.changed:
            await game.changed.wait()
            await events_queue.put({'type' : 'update', 'url' : f'/game'})

async def chronometer_events(events_queue):
    while True:
        chronometer = Chronometer.find_entry('.*')
        if chronometer is None: return
        async with chronometer.changed:
            await chronometer.changed.wait()
            await events_queue.put({'type' : 'update', 'url' : f'/chronometer'})

async def actions_events(events_queue):
    action_events = dict()
    while True:
        for action in Action.entries():
            id = action.id
            if id not in action_events:
                t = asyncio.create_task(_action_events(action, events_queue))
                action_events[id] = t
        for id, t in action_events.items():
            if t.done():
                action_events.pop(id)
        await Action.group_changed().wait()
        await events_queue.put({'type' : 'update', 'url' : f'/actions'})

async def _action_events(action, events_queue):
    while action in action.entries():
        async with action.changed:
            await action.changed.wait()
            await events_queue.put({'type' : 'update',
                                    'url' : f'/action',
                                    'id' : action.id})
            await events_queue.put({'type' : 'update', 'url' : f'/actions'})


async def conditions_events(events_queue):
    condition_events = dict()
    while True:
        for condition in Condition.entries():
            id = condition.id
            if id not in condition_events:
                t = asyncio.create_task(_condition_events(condition, events_queue))
                condition_events[id] = t
        for id, t in condition_events.items():
            if t.done():
                condition_events.pop(id)
        await Condition.group_changed().wait()
        await events_queue.put({'type' : 'update', 'url' : f'/conditions'})

async def _condition_events(condition, events_queue):
    while condition in condition.entries():
        async with condition.changed:
            await condition.changed.wait()
            await events_queue.put({'type' : 'update',
                                    'url' : f'/condition',
                                    'id' : condition.id})
            await events_queue.put({'type' : 'update', 'url' : f'/conditions'})

async def devices_events(events_queue):
    device_events = dict()
    while True:
        for device in Device.entries():
            id = device.id
            if id not in device_events:
                t = asyncio.create_task(_device_events(device, events_queue))
                device_events[id] = t
        for id, t in device_events.items():
            if t.done():
                condition_events.pop(id)
        await Device.group_changed().wait()
        await events_queue.put({'type' : 'update',
                                'url' : f'/devices'})

async def _device_events(device, events_queue):
    while device in Device.entries():
        async with device.changed:
            await device.changed.wait()
            await events_queue.put({'type' : 'update',
                                    'url' : f'/device',
                                    'id' : device.id})
            

            await events_queue.put({'type' : 'update', 'url' : f'/devices'})
