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
    def __init__(self):
        super().__init__()
        self.positions = dict()
        self.puzzles = dict()
        self.puzzles_changed = self.Condition()

    def __str__(self):
        return 'logic'

    async def _puzzle_listening(self, puzzle):
        while True:
            async with puzzle.desc_changed:
                await puzzle.desc_changed.wait()
                async with self.puzzles_changed:
                    self.puzzles_changed.notify_all()

    def find_puzzle(self, *, id=None, name=None):
        if id is not None:
            return id, self.puzzles[id]
        for device in self.puzzles.values():
            if device.name == name:
                return id, device

    def add_puzzle(self, puzzle, pos):
        _id = hex(id(puzzle))
        self.puzzles[_id] = puzzle
        self.positions[_id] = pos
        self.create_task(self._puzzle_listening(puzzle))
        logger.debug(f'{self}: {puzzle} added')

class Puzzle(Node):

    def __init__(self, name, *, initial_state='inactive'):
        super().__init__()
        self.name = name
        self.initial_state = initial_state
        self._state = None
        self.force_active = None
        self.force_completed = None
        self.paused = True
        self.description = None
        self.desc_changed = self.Condition()
        self.parents = set()
        self.conditions = set()

        self.head = lambda: None
        self.tail = lambda: None

        self.predicate = lambda: True
        self.game_flow = None

    def __str__(self):
        return f'puzzle "{self.name}" [{self.state}]'

    async def _game_flow(self):
        while True:
            async with self.desc_changed:
                while self.state == 'inactive' or self.paused:
                    await self.desc_changed.wait()
                await asyncio.ensure_finished(self.head())
                while self.state == 'active' or self.paused:
                    await self.desc_changed.wait()
                await asyncio.ensure_finished(self.tail())
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
                async with self.desc_changed:
                    await self.desc_changed.wait()

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

