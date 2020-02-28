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
from .registered import Registered


class SubProcess(Registered):

    @classmethod
    async def terminate_all(cls):
        await asyncio.gather(*{entry.terminate() for entry in cls.entries()})

    def __init__(self, name, *args, **kwargs):
        super().__init__(name)
        self.sp = None
        self._running = asyncio.Event()
        asyncio.create_task(self._start(*args, **kwargs))

    async def _start(self, *args, **kwargs):
        try:
            self.sp = await asyncio.create_subprocess_exec(*args, **kwargs)
        except BaseException as e:
            self._log_error(f'cannot exec: {e}')
            self.sp = None
            self._running.clear()
        else:
            self._running.set()
            await self.sp.wait()
            self._running.clear()

    def terminate(self):
        if self.sp is not None:
            self.sp.terminate()
            return asyncio.create_task(self.sp.wait())

    @property
    def running(self):
        return self._running.wait()

    @property
    def stdin(self):
        if self.sp is not None:
            return self.sp.stdin

    @property
    def stdout(self):
        if self.sp is not None:
            return self.sp.stdout

    @property
    def stderr(self):
        if self.sp is not None:
            return self.sp.stderr

