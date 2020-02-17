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

from . import asyncio, BoolLogic, Node
from ..logging import ANSI


class Condition(BoolLogic):

    _group = BoolLogic.Group()

    def __init__(self, name=None, func=lambda: False, *, desc=None, pos=None,
                 listens=set(), parents=set(), siblings=None, actions=set(),
                 on_true=None, on_false=None):
        super().__init__(name)
        if self._first_init:
            self.siblings = set()
            self.actions = set()
            self._listens = set()
            self._parents = set()
            self._checking = asyncio.Lock()
            self._active = asyncio.Event()
            self._satisfied = asyncio.Event()
            self._failed = asyncio.Event()
            self.force_satisfied = False
            self.msg = None
        if siblings is None: siblings = listens
        self.func = func
        self.desc = desc
        self.pos = pos
        self.add_listens(listens)
        self.add_parents(parents)
        self.siblings.update(siblings)
        self.actions.update(actions)
        self.on_true = on_true
        self.on_false = on_false

    def __str__(self):
        state = 'satisfied' if self else 'unsatisfied'
        return f'condition "{self.name}" [{state}]'

    def __bool__(self):
        return self._satisfied.is_set()

    async def __set_active(self, state: bool):
        async with self.changed:
            if state: self._active.set()
            else: self._active.clear()
            self.changed.notify_all()

    async def __set_satisfied(self, state: bool):
        async with self.changed:
            if state:
                self._satisfied.set()
                self.changed.notify_all()
                if self.on_true is not None:
                    asyncio.create_task(self.on_true())
            else:
                self._satisfied.clear()
                self.changed.notify_all()
                if self.on_false is not None:
                    asyncio.create_task(self.on_false())

    async def _check(self):
        async with self._checking:
            self._log_debug('checking:')
            for parent in self._parents:
                if not parent:
                    self._log_debug(f'parents are {ANSI["bold"]}'
                                    f'{ANSI["red"]} bad')
                    if self.active: await self.__set_active(False)
                    return
            self._log_debug(f'parents are {ANSI["bold"]}{ANSI["green"]}'
                            f'good')
            if not self.active: await self.__set_active(True)
            try:
                if asyncio.iscoroutinefunction(self.func):
                    self.msg = await self.func()
                else:
                    self.msg = self.func()
            except Exception as e:
                self._log_warning(f'failed to check condition: {e}')
                self._failed.set()
            else:
                self._failed.clear()
                if self.msg is None:
                    self._log_debug(f'function is {ANSI["bold"]}'
                                    f'{ANSI["green"]} good')
                    if not self: await self.__set_satisfied(True)
                elif self.msg is not None:
                    self._log_debug(f'function is {ANSI["bold"]}'
                                    f'{ANSI["red"]} bad')
                    if self: await self.__set_satisfied(False)

    async def __listening(self, listen: Node):
        while listen in self._listens | self._parents:
            async with listen.changed:
                await listen.changed.wait()
                await self._check()
    
    def add_parents(self, parents: BoolLogic):
        for parent in parents:
            if parent not in self._parents:
                asyncio.create_task(self.__listening(parent))
                self._parents.add(parent)
        #if parents: asyncio.create_task(self._check()) #TODO (Node.create)

    def add_listens(self, listens: BoolLogic):
        for listen in listens:
            if listen not in self._listens:
                asyncio.create_task(self.__listening(listen))
                self._listens.add(listen)
        #if listens: asyncio.create_task(self._check()) #TODO (Node.create)

    @property
    def checking(self):
        return self._checking.locked()

    @property
    def active(self):
        return self._active.is_set()

    @property
    def failed(self):
        return self._failed.is_set()


def condition(name, *args, **kwargs):
    def decorator(func):
        c = Condition.find_node(name)
        return Condition(name, func, *args, **kwargs)
    return decorator

