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

import re
from abc import ABC
from collections import defaultdict

from . import asyncio, logging


logger = logging.getLogger('escaperoom')

class Registered(ABC):

    _logger = logger
    _groups = defaultdict(dict)
    _group_changeds = defaultdict(asyncio.Event)

    descs = lambda self, name: name

    @classmethod
    def groups(cls):
        yield cls._groups[cls]
        for subcls in cls.__subclasses__():
            if subcls in cls._groups:
                yield cls._groups[subcls]

    @classmethod
    def entries(cls):
        for group in cls.groups():
            yield from group.values()

    @classmethod
    def find_entry(cls, name=None, *, id=None):
        if id is not None:
            for group in cls.groups():
                if id in group:
                    return group.get(id)
        elif name is not None:
            for entry in cls.entries():
                if entry.name and re.match(name, entry.name):
                    return entry

    @classmethod
    def __getitem__(self, key):
        entry = self.find_entry(name=key)
        if entry is None:
            raise KeyError(key)
        return entry

    @classmethod
    def group_changed(cls):
        return cls._group_changeds[cls]

    def __init__(self, name, desc=None, *, register=True):
        self.name = name
        if desc is None:
            desc = self.descs(name)
        self.desc = desc
        self.id = hex(id(self))
        self.changed = asyncio.Condition()
        if register:
            self._register()

    def _register(self):
        cls = self.__class__
        self._groups[cls][self.id] = self
        cls.group_changed().set()
        cls.group_changed().clear()

    def __str__(self):
        return f'entry "{self.name}"'

    def _log_debug(self, msg):
        self._logger.debug(f'{self}: {msg}')

    def _log_info(self, msg):
        self._logger.info(f'{self}: {msg}')

    def _log_warning(self, msg):
        self._logger.warning(f'{self}: {msg}', exc_info=True)

    def _log_error(self, msg):
        self._logger.error(f'{self}: {msg}')

    async def stop(self):
        pass

    async def reset(self):
        pass


