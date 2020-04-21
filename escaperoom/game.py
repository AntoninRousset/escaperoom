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

from pathlib import Path
import sys


class Game(Registered):

    _current = None

    options = {
            'status': 'official',
            'n_player': 4,
            'timeout_enabled': True,
            'timeout': '01:00:00'
        }

    @classmethod
    def get(cls):
        return cls._current

    def __init__(self, name, *, options={}, ready=False):
        if self._current is not None:
            raise RuntimeError('There can be only one game running')
        super().__init__(name, register=False)
        self.options.update(options)
        self._ready = ready
        self._chronometer = Chronometer('__game')
        self.main_chronometer = None
        self.give_clue = None
        Game._current = self

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

    async def _reset(self):
        await asyncio.wait({e.changed.acquire() for e in Registered.entries()})
        await asyncio.wait({entry._reset() for entry in Registered.entries()})
        for entry in Registered.entries():
            entry.changed.notify_all()
            entry.changed.release()

    async def stop(self):
        async with self.changed:
            await self._reset()
            self.changed.notify_all()

    @property
    def ready(self):
        return self._ready

    @property
    def running(self):
        return self._chronometer.running
