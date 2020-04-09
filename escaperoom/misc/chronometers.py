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

from abc import ABC
from datetime import datetime, timedelta

from . import asyncio, Misc


class Chronometer(Misc):

    def __init__(self, name):
        super().__init__(name)
        self.start_time = None #TODO list of plays and pauses
        self.end_time = None

    def __str__(self):
        return f'chronometer "{self.name}"'

    async def start(self):
        async with self.changed:
            self.start_time = datetime.today()
            self.changed.notify_all()

    async def stop(self):
        async with self.changed:
            self.end_time = datetime.today()
            self.changed.notify_all()

    async def _reset(self):
        self.start_time = None
        self.end_time = None

    @property
    def speed(self):
        return 1 if self.running else 0

    @property
    def elapsed(self):
        if self.start_time is None:
            return timedelta(0)
        elif self.end_time is None:
            return datetime.today() - self.start_time
        elif self.end_time > self.start_time:
            return self.end_time - self.start_time
        else:
            raise RuntimeError()

    @property
    def time(self):
        return self.elapsed

    @property
    def running(self):
        return self.start_time is not None and self.end_time is None

#TODO speed
#TODO multiple timeouts (-> events)

class Timer(Chronometer):

    def __init__(self, name, max_time):
        super().__init__(name)
        self._set_max_time(max_time)
        asyncio.create_task(self._timeout_checking())

    def __bool__(self):
        return self.elapsed < self._max_time

    async def _timeout_checking(self):
        while True:
            async with self.changed:
                if self:
                    try:
                        wt = self.remaining.total_seconds()
                        await asyncio.wait_on_condition(self.changed,
                                                        timeout=wt)
                    except TimeoutError:
                        pass
                else:
                    self.changed.notify_all()
                    while self:
                        await self.changed.wait()

    def _set_max_time(self, max_time):
        if not isinstance(max_time, timedelta):
            max_time = timedelta(seconds=max_time)
        self._max_time = max_time 


    async def set_max_time(self, max_time):
        async with self.changed:
            self._set_max_time(max_time)
            self.changed.notify_all()

    @property
    def speed(self):
        return -1 if self.running else 0

    @property
    def max_time(self):
        return self._max_time

    @property
    def remaining(self):
        if not self:
            return timedelta()
        return self._max_time - self.elapsed

    @property
    def time(self):
        return self.remaining

