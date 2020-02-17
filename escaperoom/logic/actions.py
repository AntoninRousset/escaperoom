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

from . import asyncio, Logic


class Action(Logic):

    def __init__(self, name=None, func=lambda: None, *, desc=None):
        super().__init__(name)
        self._running = asyncio.Lock()
        self._failed = asyncio.Event()
        self.desc = desc
        self.func = func
        self._register(Action)

    def __str__(self):
        if self.running: state = 'running'
        elif self.failed: state = 'failed'
        else: state = 'not running'
        return f'action "{self.name}" [{state}]'

    async def __call__(self, *args, **kwargs):
        async with self._running:
            try:
                if asyncio.iscoroutinefunction(self.func):
                    await self.func(*args, **kwargs)
                else:
                    self.func(*args, **kwargs)
            except Exception as e:
                self._failed.set()
                self._log_warning(f'failed : {e}')
            else:
                self._failed.clear()

    @property
    def running(self):
        return self._running.locked()

    @property
    def failed(self):
        return self._failed.is_set()


def action(name=None, *args, **kwargs):
    def decorator(func):
        a = Action.find_entry(name)
        if a is not None: return a
        return Action(name, func, *args, **kwargs)
    return decorator

