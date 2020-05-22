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

from . import asyncio
from .misc import Chronometer
from .registered import Registered
from datetime import datetime


class GameOptionEditionError(Exception):
    pass


class GameOptionList(set):

    def __init__(self, *args):
        super().__init__(GameOption(opt) for opt in args)

    def __getitem__(self, k):
        k = GameOption(k)
        if k in self:
            return k._match
        raise KeyError(k)

    def __setitem__(self, k, v):

        for opt in self:
            if opt == k:
                if not opt.editable:
                    raise GameOptionEditionError(k)
                return opt.set(v)

        raise KeyError(k)

    def mandatory(self):
        return (opt for opt in self if opt.mandatory)

    def ready(self):
        return all(self.mandatory)

    def __json__(self):
        return {opt.name: opt.value for opt in self}


class GameOption:

    def __init__(self, name, db_type=None, value=None, *, db_name=None,
                 editable=True, mandatory=False):

        if isinstance(name, GameOption):
            opt = name
            self.name = opt.name
            self.db_type = opt.db_type
            self.value = opt.value
            self.db_name = opt.db_name
            self.editable = opt.editable
            self.mandatory = opt.mandatory
        else:
            if db_type is None:
                raise ValueError('db_type must be set')
            self.name = name
            self.db_type = db_type
            self.value = value
            self.db_name = db_name
            self.editable = editable
            self.mandatory = mandatory

    def get(self):
        return self.value

    def set(self, v):
        if v is None:
            self.value = None
        else:
            self.value = v if type(v) is self.db_type else self.db_type(v)

    def __eq__(self, opt):
        if isinstance(opt, str):
            equ = (self.name == opt)
        elif isinstance(opt, GameOption):
            equ = (self.name == opt.name)
        else:
            raise TypeError(type(opt))
        if equ:
            self._match = opt
        return equ

    def __hash__(self):
        return hash(self.name)

    def __bool__(self):
        return self.value is not None


class Game(Registered):

    _current = None

    options = GameOptionList(
        GameOption('gamemaster', str, mandatory=True),
        GameOption('test', bool, mandatory=True),
        GameOption('group_name', str),
        GameOption('group_size', int),
        GameOption('leader_firstname', str),
        GameOption('leader_lastname', str),
        GameOption('leader_email', str),
        GameOption('leader_postcode', int),
        GameOption('planned_date', datetime, datetime(2000, 10, 15, 13, 15)),
        GameOption('comments', str),
    )

    @classmethod
    def get(cls):
        return cls._current

    def __init__(self, name, room, *, ready=False):

        if self._current is not None:
            raise RuntimeError('There can be only one game running')

        super().__init__(name, register=False)
        self.room = room

        self.ended = asyncio.Event()

        self._chronometer = Chronometer('__game')
        self.main_chronometer = None
        self.give_clue = None
        Game._current = self
        self.data = None

    def __str__(self):
        return f'game "{self.name}"'

    def __bool__(self):
        return self.running

    async def update_options(self, **kwargs):
        async with self.changed:
            for k, v in kwargs.items():
                self.options[k] = v
            self.changed.notify_all()

    async def start(self):
        async with self.changed:
            await self._chronometer.start()
            self.changed.notify_all()
            asyncio.ensure_future(self.run_room())

    async def run_room(self):
        state = self.room
        while state is not None:
            try:
                if isinstance(state, list):
                    state = await state[0].activate(target=state[1:])
                else:
                    state = await state.activate()
            except:
                import logging
                logging.exception('Room failed')
                state = self.room

    async def _reset(self):
        await asyncio.wait({e.changed.acquire() for e in Registered.entries()})
        await asyncio.wait({entry._reset() for entry in Registered.entries()})
        for entry in Registered.entries():
            entry.changed.notify_all()
            entry.changed.release()

    async def stop(self):
        async with self.changed:
            await self._reset()
            self.changed.notify_all()

    async def end(self):
        self.ended.set()

    @property
    def ready(self):
        return self.options.ready()

    @property
    def running(self):
        return self._chronometer.running

    def get_story(self):
        return {
            'states': {s.__qualname__: s.__json__()
                       for s in self.room.all_states}
        }

    def get_by_id(self, obj_id):

        obj_id = obj_id.split('.')
        obj = self.room

        # check room name
        if obj_id[0] != obj.__name__:
            raise ValueError(f'Game room is not {obj_id[0]} but '
                             f'{obj.__name__}')

        for s in obj_id[1:]:
            obj = getattr(obj, s)

        return obj

    def get_target_by_state_id(self, state_id):

        state_id = state_id.split('.')
        target = [self.room]

        # check room name
        if state_id[0] != self.room.__name__:
            raise ValueError(f'Game room is not {state_id[0]} but '
                             f'{self.room.__name__}')

        for s in state_id[1:]:
            target += [getattr(target[-1], s)]

        return target

    def activate_state(self, state_id):
        target = self.get_target_by_state_id(state_id)
        self.room.goto(target)

    def __json__(self):
        return {
            'running': self.running,
            'name': self.name,
            'start_time': self._chronometer.start_time,
            'end_time': self._chronometer.end_time,
            'options': self.options,
        }
