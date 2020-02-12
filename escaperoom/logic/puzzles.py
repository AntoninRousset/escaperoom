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

from . import asyncio, BoolLogic, Condition, Logic, Node

class Puzzle(BoolLogic):

    _group = BoolLogic.Group()

    def __init__(self, name=None, *, desc=None, parents=set(), conditions=set(),
                 actions=set(), tails=set(), heads=set(), pos=None):
        super().__init__(name)
        if self._first_init:
            self._parents = set()
            self._conditions = set()
            self.actions = set()
            self.force_active = False
            self._satisfied = asyncio.Event()
            self.force_satisfied = False
            asyncio.create_task(self.__flow())
        self.desc = desc
        self.add_parents(parents)
        self.add_conditions(conditions)
        self.actions.update(actions)
        self.pos = pos
        self._active = asyncio.Event()

    def __str__(self):
        state = 'done' if self else ('active' if self.active else 'inactive')
        return f'puzzle "{self.name}" [{state}]'

    def __bool__(self):
        return self.active and self.satisfied

    def __parents_check(self):
        for parent in self._parents:
            if parent: return True
        return False

    def __conditions_check(self):
        for condition in self._conditions:
            if not condition: return False
        return True

    async def __flow(self):
        while True:
            while not self.active:
                async with self.changed:
                    await self.changed.wait()
            await self._run_heads()
            while not self:
                async with self.changed:
                    await self.changed.wait()
            await self._run_tails()
            while self:
                async with self.changed:
                    await self.changed.wait()

    async def __parent_listening(self, parent: Node):
        while parent in self._parents:
            async with parent.changed:
                if self.active and not self.__parents_check():
                    async with self.changed:
                        self._active.clear()
                        self.changed.notify_all()
                elif not self.active and self.__parents_check():
                    async with self.changed:
                        self._active.set()
                        self.changed.notify_all()
                await parent.changed.wait()

    async def __condition_listening(self, condition: Condition):
        while condition in self._conditions:
            async with condition.changed:
                if not self.satisfied and self.__conditions_check():
                    async with self.changed:
                        self._satisfied.set()
                        self.changed.notify_all()
                    await asyncio.gather(*(self._tail(t) for t in set(self.tails)))
                await condition.changed.wait()

    async def _run_heads(self):
        async def _run_head(head):
            try:
                return await head()
            except Exception as e:
                self._log_warning(f'failed to run head: {e}')
        await asyncio.gather(*(_run_head(head) for head in set(self.heads)))

    async def _run_tails(self):
        async def _run_tail(tail):
            try:
                return await tail()
            except Exception as e:
                self._log_warning(f'failed to run tail: {e}')
        await asyncio.gather(*(_run_tail(tail) for tail in set(self.tails)))

    def add_parents(self, parents: Logic):
        for parent in parents:
            if parent not in self._parents:
                self._parents.add(parent)
                asyncio.create_task(self.__parent_listening(parent))

    def add_conditions(self, conditions: Logic):
        for condition in conditions:
            if condition not in self._conditions:
                self._conditions.add(condition)
                asyncio.create_task(self.__condition_listening(condition))

    @property
    def active(self) -> bool:
        return True if self.force_active else self._active.is_set()

    @property
    def satisfied(self) -> bool:
        return True if self.force_satisfied else self._satisfied.is_set()

'''
class Puzzle(Logic):

    _group = dict()

    def __init__(self, name, *, desc=None, actions=set(), conditions=set(), pos=None
                 heads=set(), tails=set(), parents=set()):
        super().__init__(name)
        self.desc = desc
        self._state = None
        self.force_active = None
        self.force_completed = None
        self.paused = True
        self.desc_changed = self.Condition()
        self.parents = set()
        self.conditions = set()

        self.heads = heads
        self.tails = tails

        self.game_flow = None

        self.pos = pos

        {self.add_parent(parent) for parent in parents}
        {self.add_condition(condition) for condition in conditions}

        self._register()

    def __str__(self):
        return f'puzzle "{self.name}" [{self.state}]'

    async def _game_flow(self):
        while True:
            async with self.desc_changed:
                while self.state == 'inactive' or self.paused:
                    await self.desc_changed.wait()
                try:
                    await asyncio.ensure_finished(self.head())
                except Exception as e:
                    self._log_error(f'head error: {e}')
                while self.state == 'active' or self.paused:
                    print('active')
                    await self.desc_changed.wait()
                try:
                    await asyncio.ensure_finished(self.tail())
                except Exception as e:
                    self._log_error(f'tail error: {e}')
                while self.state == 'completed' or self.paused:
                    await self.desc_changed.wait()

    async def _parent_listening(self, parent):
        while True:
            async with parent.desc_changed:
                if self.state == 'inactive' and parent.state is 'completed':
                    async with self.desc_changed:
                        self._state = 'active'
                        self.desc_changed.notify_all()
                await parent.desc_changed.wait()

    async def _cond_listening(self, cond):
        while True:
            if self.state == 'active':
                await self.check_conds()
                await cond.changed.wait()
            else:
                await self.changed.wait()

    def add_parent(self, parent):
        self.parents.add(parent)
        self.create_task(self._parent_listening(parent))

    def add_condition(self, cond):
        self.conditions.add(cond)
        self.create_task(self._cond_listening(cond))

    async def check_conds(self):
        try:
            if not self.predicate():
                return
        except Exception as e:
            return loggger.debug(f'{self}: predicate error: {e}')
        async with self.desc_changed:
            self._state = 'completed'
            self.desc_changed.notify_all()

    async def pause(self):
        async with self.desc_changed:
            self.paused = True
            self.desc_changed.notify_all()

    async def play(self):
        async with self.desc_changed:
            self.paused = False
            self.desc_changed.notify_all()

    async def stop(self):
        await self.pause()
        async with self.desc_changed:
            if self.game_flow is not None:
                self.game_flow.cancel()
            self.desc_changed.notify_all()

    async def reset(self):
        async with self.desc_changed:
            self.paused = True
            self._state = self.initial_state
            self.force_activate = False
            self.force_completed = False
            self.game_flow = self.create_task(self._game_flow())
            self.desc_changed.notify_all()

    @property
    def state(self):
        if self.force_completed:
            return 'completed'
        if self.force_active and self._state == 'inactive':
            return 'active'
        return self._state
'''
