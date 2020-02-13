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


class Condition(BoolLogic):

    _group = BoolLogic.Group()

    def __init__(self, name=None, func=lambda: False, *, desc=None, parents=set(),
                 listens=set(), on_change=lambda s: None):
        super().__init__(name)
        if self._first_init:
            self._listens = set()
            self._parents = set()
            self._checking = asyncio.Lock()
            self._satisfied = asyncio.Event()
            self.force_satisfied = False
            self.msg = None
        self.func = func
        self.desc = desc
        self.add_parents(parents)
        self.add_listens(listens)
        self.on_change = on_change

    def __str__(self):
        state = 'satisfied' if self.satisfied else 'unsatisfied'
        return f'condition "{self.name}" [{state}]'

    def __bool__(self):
        return self.satisfied

    async def _check(self):
        async with self._checking:
            for parent in self._parents:
                if not parent: return False
            try:
                if asyncio.iscoroutinefunction(self.func):
                    self.msg = await self.func()
                else:
                    self.msg = self.func()
                self.failed.clear()
            except Exception as e:
                self._log_warning(f'failed to check condition: {e}')
                self.msg = 'Error'
                self.failed.set()
            finally:
                if not self.satisfied.is_set() and self.msg is None:
                    async with self.changed:
                        self.satisfied.set()
                        self.changed.notify_all()
                    await self.on_change(True)
                elif self.satisfied.is_set() and self.msg is not None:
                    async with self.changed:
                        self.satisfied.clear()
                        self.changed.notify_all()
                    await self.on_change(False)

    async def __listening(self, listen: Node):
        while listen in self._listens:
            async with listen.changed:
                await self._check()
                await listen.changed.wait()
    
    def add_parents(self, parents: BoolLogic):
        for parent in parents:
            if parent not in self._parents:
                asyncio.create_task(self.__listening(parent))
                self._parents.add(parent)

    def add_listens(self, listens: BoolLogic):
        for listen in listens:
            if listen not in self._listens:
                asyncio.create_task(self.__listening(listen))
                self._listens.add(listen)

    @property
    def checking(self):
        return self._checking.locked()

    @property
    def satisfied(self):
        return True if self.force_satisfied else self._satisfied.is_set()


def condition(name, *args, **kwargs):
    def decorator(func):
        c = Condition.find_node(name)
        return Condition(name, *args, **kwargs)
    return decorator

