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

from . import action, asyncio, BoolLogic
from ..logging import ANSI
from ..network.devices import NotReady
from ..utils import ensure_iter

class Condition(BoolLogic):

    def __init__(self, name=None, func=None, *, desc=None, pos=None,
                 listens=set(), parents=set(), actions=set(), args=tuple(),
                 on_trues=set(), on_falses=set(), state=None):
        super().__init__(name, desc)
        self._checking = asyncio.Lock()
        self._initial_state = state
        self.func = func
        self.args = tuple(args)
        self.pos = pos
        self._listens = set()
        self.add_listens(listens)
        self._parents = set()
        self.add_parents(parents)
        self.actions = set(ensure_iter(actions))
        self.on_trues = set(ensure_iter(on_trues))
        self.on_falses = set(ensure_iter(on_falses))
        asyncio.run_until_complete(self.reset())

    def __str__(self):
        return f'condition "{self.name}" [{bool(self)}]'

    def __bool__(self):
        return self.state == True

    def __check_parents(self):
        if not self._parents:
            return None
        for parent in self._parents:
            if not parent:
                self._log_debug(f'parents are {ANSI["bold"]}{ANSI["red"]} bad')
                self.msg = f'parent "{parent.name}" pas prêt'
                return False
        self._log_debug(f'parents are {ANSI["bold"]}{ANSI["green"]} good')
        return True

    def _check_func(self):
        try:
            self.msg = self.func(*self.args)
        except NotReady:
            self._log_debug(f'not ready to check')
            return
        except Exception as e:
            self._log_warning(f'failed to check condition: {e}')
            if not self.failed:
                self._failed.set()
                self.changed.notify_all()
            return
        finally:
            color = 'green' if self.msg is None else 'red'
            state = 'good' if self.msg is None else 'bad'
            self._log_debug(f'function is {ANSI["bold"]} {ANSI[color]} {state}')
            return self.msg is None

    async def _check(self, acquired=False):
        if not acquired:
            await self.changed.acquire()
        try:
            async with self._checking:
                self._log_debug('checking:')
                self.changed.notify_all()
                await asyncio.sleep(0)
                state = self.__check_parents()
                if ( state or state is None ) and self.func is not None:
                    state = self._check_func()
                if state is not None and await self._set_state(state):
                    self.changed.notify_all()
        except Exception:
            pass
        finally:
            if not acquired:
                self.changed.release()

    async def __listening(self, listen):
        while listen in self._listens | self._parents:
            async with listen.changed:
                await listen.changed.wait()
                await self._check(listen.changed == self.changed)
    
    async def abort_on_trues(self):
        await asyncio.gather(*{on_true.abort() for on_true in self.on_trues})

    async def abort_on_falses(self):
        await asyncio.gather(*{on_false.abort() for on_false in self.on_falses})

    def add_parents(self, parents: BoolLogic):
        parents = set(ensure_iter(parents))
        for parent in parents:
            if parent not in self._parents:
                asyncio.create_task(self.__listening(parent))
                self._parents.add(parent)
        asyncio.create_task(self._check())

    def add_listens(self, listens: BoolLogic):
        listens = set(ensure_iter(listens))
        for listen in listens:
            if listen not in self._listens:
                asyncio.create_task(self.__listening(listen))
                self._listens.add(listen)
        asyncio.create_task(self._check())

    async def _set_state(self, state):
        if state == True:
            if self.state is None or self.state == False:
                self._state = state
                self._log_info(f'became {ANSI["green"]} good')
                if not self.desactivated:
                    {asyncio.create_task(co()) for co in self.on_trues}
                return True
        elif state == False:
            if self.state is None or self.state == True:
                self._state = state
                self._log_info(f'became {ANSI["red"]} bad')
                if not self.desactivated:
                    {asyncio.create_task(co()) for co in self.on_falses}
                return True
        return False

    async def set_state(self, state):
        async with self.changed:
            if await self._set_state(state):
                self.changed.notify_all()

    async def reset(self):
        async with self.changed:
            self._failed = False
            self._desactivated = False
            self._force = None
            self.msg = None
            self._state = self._initial_state

    async def force(self, state: bool):
        async with self.changed:
            self._force = state
            await self._check(acquired=True)

    async def restore(self):
        async with self.changed:
            self._force = None
            await self._check(acquired=True)

    async def activate(self):
        async with self.changed:
            self._desactivated = False
            self.changed.notify_all()
            await asyncio.sleep(0)

    async def desactivate(self):
        async with self.changed:
            self._desactivated = True
            self.changed.notify_all()
            await asyncio.sleep(0)

    def on_true(self, *args, **kwargs):
        def decorator(func):
            a = action(*args, **kwargs)(func)
            self.on_trues.add(a)
            self.actions.add(a)
            return a
        return decorator

    def on_false(self, *args, **kwargs):
        def decorator(func):
            a = action(*args, **kwargs)(func)
            self.on_falses.add(a)
            self.actions.add(a)
            return a
        return decorator

    @property
    def state(self):
        if self._force is True:
            return True
        if self._force is False:
            return False
        return self._state

    @property
    def checking(self):
        return self._checking.locked()

    @property
    def failed(self):
        return self._failed

    @property
    def desactivated(self):
        return self._desactivated


def condition(name, *args, **kwargs):
    from functools import partial
    def decorator(func):
        c = Condition.find_entry(name)
        return Condition(name, func, *args, **kwargs)
    return decorator

