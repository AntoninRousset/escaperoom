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

    def __init__(self, name, *, options={}, ready=False):
        if Game.entries():
            raise RuntimeError('There can be only one game running')
        super().__init__(name)
        self.options.update(options)
        self._ready = ready
        self._chronometer = Chronometer()
        self._register(Game)

    def __str__(self):
        return f'game "{self.name}"'

    def __bool__(self):
        return self.running

    async def set_ready(self):
        async with self.changed:
            self._ready = True
            self.changed.notify_all()

    async def start(self, options):
        async with self._chronometer.changed:
            self._chronometer.start()
            self._chronometer.changed.notify_all()

    async def stop(self, options):
        async with self._chronometer.changed:
            self._chronometer.stop()
            self._chronometer.changed.notify_all()

    @property
    def ready(self):
        return self._ready

    @property
    def running(self):
        return self._chronometer.is_running()
