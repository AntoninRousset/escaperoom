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
from ..logic import Puzzle
from ..network import Device

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

async def generator(game):
    if game not in events_queues:
        events_queue = SharedQueue()
        categories = {game_events, chronometer_events, puzzles_events, devices_events}
        for events in categories:
            asyncio.create_task(events(game, events_queue))
        events_queues[game] = events_queue
    while True:
        q = events_queues[game]
        try:
            event = events_queues[game].get_nowait()
        except asyncio.QueueEmpty:
            event = await events_queues[game].get()
        yield event

async def game_events(game, events_queue):
    while True:
        await game.changed.wait()
        await events_queue.put({'type' : 'update', 'loc' : f'/{game.name}/game'})

async def chronometer_events(game, events_queue):
    while True:
        await game.changed.wait()
        await events_queue.put({'type' : 'update',
                                'loc' : f'/{game.name}/chronometer'})

async def puzzles_events(game, events_queue):
    puzzle_events = dict()
    while True:
        for puzzle in Puzzle.nodes():
            id = puzzle.id
            if id not in puzzle_events:
                t = puzzle.create_task(_puzzle_events(game, id, events_queue))
                puzzle_events[id] = t
        for id, t in puzzle_events.items():
            if t.done():
                puzzle_events.pop(id)
        await Puzzle.group_changed.wait()
        await events_queue.put({'type' : 'update', 'loc' : f'/{game.name}/puzzles'})

async def _puzzle_events(game, id, events_queue):
    while True:
        await Puzzle.find_node(id=id).changed.wait()
        await events_queue.put({'type' : 'update',
                                'loc' : f'/{game.name}/puzzle?id={id}'})

async def devices_events(game, events_queue):
    device_events = dict()
    while True:
        for device in Device.nodes():
            id = device.id
            if id not in device_events:
                t = asyncio.create_task(_device_events(game, id, events_queue))
                device_events[id] = t
        for id, t in device_events.items():
            if t.done():
                puzzle_events.pop(id)
        await Device.group_changed.wait()
        await events_queue.put({'type' : 'update',
                                'loc' : f'/{game.name}/devices'})

async def _device_events(game, id, events_queue):
    while True:
        await Device.find_node(id=id).changed.wait()
        await events_queue.put({'type' : 'update',
                                'loc' : f'/{game.name}/device?id={id}'})

