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
                 on_trues=set(), on_falses=set()):
        super().__init__(name, desc)
        self._checking = asyncio.Lock()
        self._failed = True
        self._desactivated = False
        self._force = None
        self.msg = None
        self._state = None
        self.func = func
        self.args = tuple(args)
        self.pos = pos
        self._listens = set()
        self.add_listens(set(ensure_iter(listens)))
        self._parents = set()
        self.add_parents(set(ensure_iter(parents)))
        self.actions = set(ensure_iter(actions))
        self.on_trues = set(ensure_iter(on_trues))
        self.on_falses = set(ensure_iter(on_falses))

    def __str__(self):
        state = 'satisfied' if self else 'unsatisfied'
        return f'condition "{self.name}" [{state}]'

    def __bool__(self):
        if self._force is True:
            return True
        elif self._force is False:
            return False
        else:
            return False if self._state is None else self._state

    async def __check_parents(self):
        for parent in self._parents:
            if not parent:
                self._log_debug(f'parents are {ANSI["bold"]}{ANSI["red"]} bad')
                return 'parent unsatisfied'
        self._log_debug(f'parents are {ANSI["bold"]}{ANSI["green"]} good')

    async def __check_func(self):
        if self.func is not None:
            if asyncio.iscoroutinefunction(self.func):
                return await self.func(*self.args)
            else:
                return self.func(*self.args) #TODO? accept only coroutine

    async def _check(self):
        async with self.changed:
            async with self._checking:
                self._log_debug('checking:')
                self.changed.notify_all()
                msg = await self.__check_parents()
                if msg is None:
                    try:
                        msg = await self.__check_func()
                    except NotReady:
                        return self._log_debug(f'not ready to check')
                    except Exception as e:
                        self._log_warning(f'failed to check condition: {e}')
                        if not self.failed:
                            self.changed.notify_all()
                        return self._failed.set()
                self.msg = msg
                if self.msg is None or self._force is True:
                    self._log_debug(f'function is {ANSI["bold"]}'
                                    f'{ANSI["green"]} good')
                    if not self._state or self._state is None:
                        self._state = True
                        self.changed.notify_all()
                        if not self.desactivated:
                            {asyncio.create_task(co()) for co in self.on_trues}
                elif self.msg is not None or self._force is False:
                    self._log_debug(f'function is {ANSI["bold"]}'
                                    f'{ANSI["red"]} bad')
                    if self._state or self._state is None:
                        self._state = False
                        self.changed.notify_all()
                        if not self.desactivated:
                            {asyncio.create_task(co()) for co in self.on_falses}

    async def __listening(self, listen):
        while listen in self._listens | self._parents:
            async with listen.changed:
                await listen.changed.wait()
                await self._check()
    
    def add_parents(self, parents: BoolLogic):
        for parent in parents:
            if parent not in self._parents:
                asyncio.create_task(self.__listening(parent))
                self._parents.add(parent)
        asyncio.create_task(self._check())

    def add_listens(self, listens: BoolLogic):
        for listen in listens:
            if listen not in self._listens:
                asyncio.create_task(self.__listening(listen))
                self._listens.add(listen)
        asyncio.create_task(self._check())

    async def force(self, state: bool):
        async with self.changed:
            self._force = state
            self.changed.notify_all()
        await self._check()

    async def restore(self):
        async with self.changed:
            self._force = None
            self.changed.notify_all()
        await self._check()

    async def activate(self):
        async with self.changed:
            self._desactivated = False
            self.changed.notify_all()

    async def desactivate(self):
        async with self.changed:
            self._desactivated = True
            self.changed.notify_all()

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

