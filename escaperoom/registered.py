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
from abc import ABC, abstractclassmethod
from collections import defaultdict

from . import asyncio, logging


logger = logging.getLogger('escaperoom')

class Registered(ABC):

    _logger = logger
    _groups = defaultdict(dict)
    _group_changeds = defaultdict(asyncio.Event)

    descs = lambda self, name: name

    @classmethod
    def entries(cls):
        return cls._groups[cls].values()

    @classmethod
    def find_entry(cls, name=None, *, id=None):
        if id: return cls._groups[cls].get(id)
        if name:
            for entry in cls.entries():
                if entry.name and re.match(name, entry.name): return entry

    @classmethod
    def group_changed(cls):
        return cls._group_changeds[cls]

    def __init__(self, name, desc=None):
        self.name = name
        if desc is None:
            desc = self.descs(name)
        self.desc = desc
        self.id = hex(id(self))
        self.changed = asyncio.Condition()

    def _register(self, cls):
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
        self._logger.warning(f'{self}: {msg}')

    def _log_error(self, msg):
        self._logger.error(f'{self}: {msg}')

