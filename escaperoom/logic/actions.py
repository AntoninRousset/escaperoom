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


async def dummy(*args, **kwargs):
    pass

class Action(Logic):

    def __init__(self, name=None, func=None, *, desc=None, task=False,
                 args=None):
        super().__init__(name, desc)
        self._running = asyncio.Lock()
        self._failed = asyncio.Event()
        self.func = func
        self.args = tuple() if args is None else args
        self._task = asyncio.create_task(dummy())
        self._desactivated = asyncio.Event()
        self._success = asyncio.Event()
        if task: asyncio.create_task(self())

    def __str__(self):
        if self.running: state = 'running'
        elif self.failed: state = 'failed'
        else: state = 'not running'
        return f'action "{self.name}" [{state}]'

    def __bool__(self):
        return self._success.is_set()

    async def __call__(self):
        async with self._running:
            async with self.changed:
                if self.desactivated:
                    return
                self._log_debug('start')
                self._success.clear()
                self.changed.notify_all()
                try:
                    if self.func is not None:
                        self._task = asyncio.create_task(self.func(*self.args))
                        await self._task
                except asyncio.CancelledError:
                    self._log_info('cancelled')
                except Exception as e:
                    self._failed.set()
                    self._log_warning(f'failed : {e}')
                else:
                    self._failed.clear()
                    self._success.set()
                self._log_debug('end')
                self.changed.notify_all()

    async def abort(self):
        self._task.cancel()
        await asyncio.sleep(0)

    async def activate(self):
        async with self.changed:
            self._desactivated.clear()
            self.changed.notify_all()

    async def desactivate(self):
        async with self.changed:
            self._desactivated.set()
            self.changed.notify_all()

    @property
    def running(self):
        return self._running.locked()

    @property
    def failed(self):
        return self._failed.is_set()

    @property
    def desactivated(self):
        return self._desactivated.is_set()


def action(name=None, *args, **kwargs):
    def decorator(func):
        a = Action.find_entry(name)
        if a is not None: return a
        return Action(name, func, *args, **kwargs)
    return decorator

