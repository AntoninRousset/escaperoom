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
    while True:
        await game.logic.changed.wait()
        await events_queue.put({'type' : 'update', 'loc' : f'/{game.name}/puzzles'})

async def _puzzle_events(game, uid, events_queue):
    while True:
        await game.logic.puzzles[uid].changed.wait()
        await events_queue.put({'type' : 'update',
                                'loc' : f'/{game.name}/puzzle?id={uid}'})

async def devices_events(game, events_queue):
    devices = dict()
    while True:
        async with game.network.devices_changed:
            for uid in game.network.devices:
                if uid not in devices:
                    t = asyncio.create_task(_device_events(game, uid, events_queue))
                    devices[uid] = t
            await game.network.devices_changed.wait()
            await events_queue.put({'type' : 'update',
                                    'loc' : f'/{game.name}/devices'})

async def _device_events(game, uid, events_queue):
    while True:
        await game.network.devices[uid].changed.wait()
        await events_queue.put({'type' : 'update',
                                'loc' : f'/{game.name}/device?id={uid}'})

