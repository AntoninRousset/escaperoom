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

from . import config 
from .node import Node

def log_debug(msg):
    if config['DEFAULT'].getboolean('log_debug', False):
        print(msg)

class Logic(Node):
    def __init__(self):
        super().__init__()
        self.positions = dict()
        self.puzzles = dict()
        self.puzzles_changed = self.Condition()

    async def _puzzle_listening(self, puzzle):
        while True:
            async with puzzle.desc_changed:
                await puzzle.desc_changed.wait()
                async with self.puzzles_changed:
                    self.puzzles_changed.notify_all()

    def add_puzzle(self, puzzle, pos):
        uid = hex(id(puzzle))
        self.puzzles[uid] = puzzle
        self.positions[uid] = pos
        self.create_task(self._puzzle_listening(puzzle))
        log_debug('Logic: Puzzle added')
        return uid

class Puzzle(Node):

    def __init__(self, name, *, initial_state='inactive'):
        super().__init__()
        self.name = name
        self.initial_state = initial_state
        self.state = None
        self.description = None
        self.desc_changed = self.Condition()
        self.parents = set()
        self.conditions = set()

        self.head = lambda: None
        self.tail = lambda: None

        self.predicate = lambda: False
        self.game_flow = None

    async def _game_flow(self):
        while True:
            print(f'{self.name} game_flow', self.state, self.initial_state)
            async with self.desc_changed:
                while self.state == 'inactive':
                    await self.desc_changed.wait()
                print('head')
                self.head() #TODO if its a future, wait for it
                while self.state == 'active':
                    await self.desc_changed.wait()
                self.tail() #TODO same
                while self.state == 'completed':
                    await self.desc_changed.wait()

    async def _parent_listening(self, parent):
        while True:
            async with parent.desc_changed:
                if self.state is 'inactive' and parent.state is 'completed':
                    async with self.desc_changed:
                        self.state = 'active'
                        self.desc_changed.notify_all()
                await parent.desc_changed.wait()

    async def _cond_listening(self, cond):
        while True:
            if self.state is 'active':
                await self.check_conds()
                try:
                    async with cond.desc_changed:
                        await cond.desc_changed.wait()
                except Exception as e:
                    print(e)
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
            return log_debug(f'Puzzle: Predicate error: {e}')
        async with self.desc_changed:
            self.state = 'completed'
            self.desc_changed.notify_all()

    async def stop(self):
        if self.game_flow is not None:
            await self.game_flow.cancel()

    async def reset(self):
        async with self.desc_changed:
            self.state = self.initial_state
            self.desc_changed.notify_all()
        self.game_flow = self.create_task(self._game_flow())

    @property
    def predicate(self):
        return self._predicate

    @predicate.setter
    def predicate(self, val):
        self._predicate = val
        #self.create_task(self.check_conds())

