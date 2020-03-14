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

from . import asyncio
from .misc import Chronometer
from .registered import Registered

from datetime import datetime, timedelta


class Game(Registered):

    options = {
            'status' : 'official',
            'n_player' : 4,
            'timeout_enabled' : True,
            'timeout' : '01:00:00'
        }

    @classmethod
    def get(cls):
        return next(cls.entries())

    def __init__(self, name, *, options={}, ready=False):
        if set(Game.entries()):
            raise RuntimeError('There can be only one game running')
        super().__init__(name)
        self.options.update(options)
        self._ready = ready
        self._chronometer = Chronometer('__game')
        self.main_chronometer = None
        self.give_clue = None

    def __str__(self):
        return f'game "{self.name}"'

    def __bool__(self):
        return self.running

    async def set_ready(self, state=True):
        async with self.changed:
            self._ready = state
            self.changed.notify_all()

    async def start(self, options):
        async with self.changed:
            await self._chronometer.start()
            self.changed.notify_all()

    async def stop(self, options):
        pass
        #await asyncio.wait(entry.stop() for entry in Registered.entries())

    async def reset(self, options):
        pass
        #await asyncio.wait(entry.reset() for entry in Registered.entries())

    @property
    def ready(self):
        return self._ready

    @property
    def running(self):
        return self._chronometer.running
