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

import asyncio
from datetime import datetime, timedelta

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
        self.default_settings = dict()
        self.start_time = None
        self.end_time = datetime.today()

    async def new_game(self, settings=dict()):
        self.start_time = None
        self.end_time = None
        self.parse_settings(settings)
        cs = {self.create_task(p.reset()) for p in self.logic.puzzles.values()}
        await asyncio.wait(cs)
        self.game_id = database.write_game(self, new=True)

    def parse_settings(settings):
        pass

    def start_chronometer(self):
        self.start_time = datetime.today() 
        database.write_game(self)

    def stop_chronometer(self):
        self.end_time = datetime.today() 
        database.write_game(self)

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
    def ready(self):
        'ready to start game (minimum to go)'
        return True

    @property
    def running(self):
        if self.end_time is None:
            return True
        return False

    @property
    def issues(self):
        return 'list of issues'
