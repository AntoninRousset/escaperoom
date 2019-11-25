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

import datetime

from .logic import Logic
from .misc import Misc 
from .node import Node
from .network import Network
from . import database

class Game(Node):
    def __init__(self, name):
        super().__init__()
        self.name = name
        self.network = Network() 
        self.logic = Logic()
        self.misc = Misc()
        self.game_id = None
        self.start_time = None
        self.stop_time = None

    async def reset(self):
        self.start_time = None
        self.stop_time = None
        cs = (puzzle.reset() for puzzle in self.logic.puzzles.values())
        await asyncio.gather(cs)
        self.game_id = database.write_game(self, new=True)

    def start_counter(self):
        self.start_time = datetime.today() 
        database.write_game(self)

    def stop_counter(self):
        self.stop_time = datetime.today() 
        database.write_game(self)

    @property
    def counter(self):
        if self.start_time is None:
            return datetime.timedelta(0)
        elif self.stop_time is None:
            return datetime.today() - self.start_time
        elif self.stop_time > self.start_time:
            return self.stop_time - self.start_time
        else:
            raise RuntimeError()

    @property
    def ready(self):
        'ready to start game (minimum to go)'
        return True

    @property
    def issues(self):
        return 'list of issues'
