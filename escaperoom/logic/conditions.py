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


class Condition(BoolLogic):

    def __init__(self, name=None, func=lambda: False, *, desc=None, pos=None,
                 listens=set(), parents=set(), siblings=None, actions=set(),
                 on_trues=None, on_falses=None, args=None):
        super().__init__(name)
        self.siblings = set()
        self.actions = set()
        self._listens = set()
        self._parents = set()
        self._checking = asyncio.Lock()
        self._active = asyncio.Event()
        self._satisfied = asyncio.Event()
        self._failed = asyncio.Event()
        self.force_satisfied = False
        self._desactivated = asyncio.Event()
        self.msg = ''
        self.func = func
        self.args = args
        self.desc = desc
        self.pos = pos
        self.add_listens(listens)
        self.add_parents(parents)
        if siblings is None:
            siblings = {c for c in listens if isinstance(c, Condition)}
        self.siblings.update(siblings)
        self.actions.update(actions)
        if on_trues is None: on_trues = set()
        self.on_trues = on_trues
        if on_falses is None: on_falses = set()
        self.on_falses = on_falses
        self._register(Condition)

    def __str__(self):
        state = 'satisfied' if self else 'unsatisfied'
        return f'condition "{self.name}" [{state}]'

    def __bool__(self):
        return self.msg is None

    async def __set_active(self, state: bool):
        async with self.changed:
            if state: self._active.set()
            else: self._active.clear()
            self.changed.notify_all()

    async def _check(self):
        async with self._checking:
            self._log_debug('checking:')
            for parent in self._parents:
                if not parent:
                    self._log_debug(f'parents are {ANSI["bold"]}{ANSI["red"]}'
                                    f'bad')
                    if self.active: await self.__set_active(False)
                    return
            self._log_debug(f'parents are {ANSI["bold"]}{ANSI["green"]} good')
            if not self.active: await self.__set_active(True)
            try:
                if asyncio.iscoroutinefunction(self.func):
                    if self.args is None:
                        msg = await self.func()
                    else:
                        msg = await self.func(self.args)
                else:
                    if self.args is None:
                        msg = self.func()
                    else:
                        msg = self.func(self.args)
            except NotReady:
                self._log_debug(f'not ready to check')
                print(self.msg, '->', bool(self))
            except Exception as e:
                self._log_warning(f'failed to check condition: {e}')
                async with self.changed:
                    if not self.failed:
                        self.changed.notify_all()
                    self._failed.set()
            else:
                async with self.changed:
                    previous_state = bool(self)
                    self.msg = msg
                    if self.msg is None:
                        print(self, 'winner!', msg)
                        self._log_debug(f'function is {ANSI["bold"]}'
                                        f'{ANSI["green"]} good')
                        if not previous_state or self.failed:
                            self.changed.notify_all()
                        if not previous_state and not self.desactivated:
                            {asyncio.create_task(co()) for co in self.on_trues}
                    elif self.msg is not None:
                        self._log_debug(f'function is {ANSI["bold"]}'
                                        f'{ANSI["red"]} bad')
                        if previous_state or self.failed:
                            self.changed.notify_all()
                        if previous_state and not self.desactivated:
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
        if parents: asyncio.create_task(self._check())

    def add_listens(self, listens: BoolLogic):
        for listen in listens:
            if listen not in self._listens:
                asyncio.create_task(self.__listening(listen))
                self._listens.add(listen)
        if listens: asyncio.create_task(self._check())

    async def activate(self):
        async with self.changed:
            self._desactivated.clear()
            self.changed.notify_all()

    async def desactivate(self):
        async with self.changed:
            self._desactivated.set()
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
    def active(self):
        return self._active.is_set()

    @property
    def failed(self):
        return self._failed.is_set()

    @property
    def desactivated(self):
        return self._desactivated.is_set()


def condition(name, *args, **kwargs):
    from functools import partial
    def decorator(func):
        c = Condition.find_entry(name)
        return Condition(name, func, *args, **kwargs)
    return decorator

