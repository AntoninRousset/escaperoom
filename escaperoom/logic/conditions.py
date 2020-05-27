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
from ..network.devices import Device, NotReady
from ..utils import ensure_iter


class Condition(BoolLogic):

    def __init__(self, name=None, func=None, *, desc=None, pos=None,
                 listens=set(), parents=set(), actions=set(), args=tuple(),
                 on_trues=set(), on_falses=set(), state=None):
        super().__init__(name, desc)
        self._initial_state = state
        self.func = func
        self.args = tuple(args)
        self.pos = pos
        self.actions = set(ensure_iter(actions))
        self.on_trues = set(ensure_iter(on_trues))
        self.on_falses = set(ensure_iter(on_falses))
        self.siblings = None  # Could be solved algorithmically
        self._listens = set()
        self.add_listens(listens)
        self._parents = set()
        self.add_parents(parents)

        self._failed = False
        self._desactivated = False
        self.msg = None
        self._force = None
        self._state = self._initial_state

        asyncio.create_task(self.check())

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
                if isinstance(parent, Device):
                    self.msg = f'device "{parent.name}" pas connecté'
                elif isinstance(parent, Condition):
                    self.msg = parent.msg
                else:
                    self.msg = f'parent "{parent.name}" pas prêt'
                return False
        self._log_debug(f'parents are {ANSI["bold"]}{ANSI["green"]} good')
        return True

    def __check_func(self):
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

    def _check(self):
        self._log_debug('checking:')
        state = self.__check_parents()
        if ( state or state is None ) and self.func is not None:
            state = self.__check_func()
        if state is not None and self._set_state(state):
            self.changed.notify_all()

    async def check(self):
        async with self.changed:
            self._check()

    async def __listening(self, listen):
        while listen in self._listens | self._parents:
            async with listen.changed:
                await listen.changed.wait()
                if listen.changed == self.changed:
                    self._check()
                else:
                    await self.check()
    
    async def abort_on_trues(self):
        await asyncio.gather(*{on_true.abort() for on_true in self.on_trues})

    async def abort_on_falses(self):
        await asyncio.gather(*{on_false.abort() for on_false in self.on_falses})

    def add_parents(self, parents: BoolLogic):
        for parent in ensure_iter(parents):
            if parent not in self._parents:
                asyncio.create_task(self.__listening(parent))
                self._parents.add(parent)

    def add_listens(self, listens: BoolLogic):
        for listen in ensure_iter(listens):
            if listen not in self._listens:
                asyncio.create_task(self.__listening(listen))
                self._listens.add(listen)

    def __state_change(self, old_state):
        if self.state == True and (old_state == False or old_state is None):
            self._log_info(f'became {ANSI["green"]} good')
            if not self.desactivated:
                {asyncio.create_task(co()) for co in self.on_trues}
            return True
        elif self.state == False and (old_state == True or old_state is None):
            self._log_info(f'became {ANSI["red"]} bad')
            if not self.desactivated:
                {asyncio.create_task(co()) for co in self.on_falses}
            return True
        return False

    def _set_state(self, state):
        old_state = self.state
        self._state = state
        return self.__state_change(old_state)

    async def set_state(self, state):
        async with self.changed:
            if self._set_state(state):
                self.changed.notify_all()

    async def _reset(self):
        self._failed = False
        self._desactivated = False
        self.msg = None
        self._force = None
        self._state = self._initial_state

    async def reset(self):
        async with self.changed:
            self._reset()
            self.changed.notify_all()

    async def force(self, state: bool): #TODO call it force_state
        async with self.changed:
            old_state = self.state
            self._force = state
            self.__state_change(old_state) #TODO? aenter for this kind of change
            self.changed.notify_all()

    async def restore(self):
        return await self.force(None)

    async def set_active(self, state):
        async with self.changed:
            self._desactivated = state == False
            self.changed.notify_all()

    async def activate(self):
        return await self.set_active(True)

    async def desactivate(self):
        return await self.set_active(False)

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
        if self._force is None:
            return self._state
        return self._force

    @property
    def failed(self):
        return self._failed

    @property
    def desactivated(self):
        return self._desactivated

    @property
    def forced(self):
        return self._force is not None


def condition(name, *args, **kwargs):
    from functools import partial
    def decorator(func):
        c = Condition.find_entry(name)
        return Condition(name, func, *args, **kwargs)
    return decorator

