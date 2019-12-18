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
from .misc import Misc 
from .node import Node
from .network import Network

class Game(Node):
    def __init__(self, name):
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
        self.misc = Misc()

    def resume_game(self):
        pass #TODO read database to resume a game

    async def new_game(self, options):
        await self.stop_game()
        async with self.desc_changed:
            cs = {self.create_task(p.reset()) for p in self.logic.puzzles.values()}
            await asyncio.wait(cs)
            self.options = options
            self.game_id = database.new_game(self.name, self.options)
            self.desc_changed.notify_all()

    async def stop_game(self):
        async with self.desc_changed:
            cs = {self.create_task(p.stop()) for p in self.logic.puzzles.values()}
            await asyncio.wait(cs)
            self.game_id = None
            self.options = None
            self.start_time = None
            self.end_time = None
            self.desc_changed.notify_all()

    def start_chronometer(self):
        self.start_time = datetime.today()
        database.game_start(self.game_id, self.start_time)

    def stop_chronometer(self):
        self.stop_time = datetime.today()
        database.game_end(self.game_id, self.stop_time)

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

