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

    _group = Logic.Group()

    def __init__(self, name=None, func=lambda: None, *, desc=None):
        super().__init__(name)
        if self._first_init:
            self._running = asyncio.Lock()
            self.failed = asyncio.Event()
        self.desc = desc
        self.func = func

    def __str__(self):
        state = 'running' if self.running else 'not running'
        return f'action "{self.name}" [{state}]'

    async def __call__(self, *args, **kwargs):
        async with self._running:
            try:
                if asyncio.iscoroutinefunction(self.func):
                    return await self.func()
                else:
                    return self.func()
            except Exception as e:
                self._log_warning(f'failed : {e}')
                self.failed.set()

    @property
    def running(self):
        return self._running.locked()


def action(name=None, *args, **kwargs):
    def decorator(func):
        a = Action.find_node(name)
        if a is not None and a.func != func:
            a._log_warning('creating action with same name but different func')
        return Action(name, *args, **kwargs)
    return decorator

