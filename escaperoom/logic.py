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

from . import asyncio, config, logging 
from .node import Node

logger = logging.getLogger('escaperoom.logic')

class Logic(Node):
    
    _logger = logger


class Puzzle(Logic):

    _group = dict()

    def __init__(self, name, *, initial_state='inactive', description='',
                 head=lambda: None, tail=lambda: None, parents=[], conditions=[],
                 predicate=lambda: True, pos=None):
        super().__init__(name)
        self.name = name
        self.initial_state = initial_state
        self._state = None
        self.force_active = None
        self.force_completed = None
        self.paused = True
        self.description = description
        self.desc_changed = self.Condition()
        self.parents = set()
        self.conditions = set()

        self.head = head
        self.tail = tail

        self.predicate = predicate
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

