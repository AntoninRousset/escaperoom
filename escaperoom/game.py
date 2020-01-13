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

from datetime import datetime, timedelta

from . import asyncio, database
from .logic import Logic
from .node import Node
from .network import Network

class Game(Node):

    games = dict()

    def __init__(self, name):
        if name in self.games:
            raise RuntimeError()
        super().__init__()
        self.name = name
        self.game_id = None
        self.default_options = {
                'status' : 'official',
                'n_player' : 4,
                'timeout_enabled' : True,
                'timeout' : '01:00:00'
            }
        self.start_time = None
        self.end_time = None
        self.desc_changed = self.Condition()
        self.network = Network() 
        self.logic = Logic()
        self.games[name] = self

    def resume_game(self):
        pass #TODO read database to resume a game

    async def new_game(self, options):
        await self.stop_game()
        async with self.desc_changed:
            await asyncio.gather(*{p.reset() for p in self.logic.puzzles.values()})
            self.options = options
            await self.play()
            self.game_id = database.new_game(self.name, self.options)
            self.desc_changed.notify_all()

    async def pause(self):
        await asyncio.gather(*{p.pause() for p in self.logic.puzzles.values()})

    async def play(self):
        await asyncio.gather(*{p.play() for p in self.logic.puzzles.values()})

    async def stop_game(self):
        async with self.desc_changed:
            await asyncio.gather(*{p.stop() for p in self.logic.puzzles.values()})
            self.game_id = None
            self.options = None
            self.start_time = None
            self.end_time = None
            self.desc_changed.notify_all()

    async def start_chronometer(self):
        async with self.desc_changed:
            self.start_time = datetime.today()
            database.game_start(self.game_id, self.start_time)
            self.desc_changed.notify_all()

    async def stop_chronometer(self):
        async with self.desc_changed:
            self.end_time = datetime.today()
            database.game_end(self.game_id, self.end_time)
            self.desc_changed.notify_all()

    @property
    def chronometer(self):
        if self.start_time is None:
            return timedelta(0)
        elif self.end_time is None:
            return datetime.today() - self.start_time
        elif self.end_time > self.start_time:
            return self.end_time - self.start_time
        else:
            raise RuntimeError()

    @property
    def running(self):
        if self.game_id is None:
            return False 
        return True

