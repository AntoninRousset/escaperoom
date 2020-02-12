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

from . import asyncio, logging


logger = logging.getLogger('escaperoom')


class Node(ABC):

    group_changed = asyncio.Event()

    @property
    @abstractclassmethod
    def _group(cls):
        raise NotImplementedError

    @classmethod
    def nodes(cls):
        return cls._group.values()

    @classmethod
    def find_node(cls, name=None, *, id=None):
        if id is not None:
            return cls._group[id]
        if name is not None:
            for node in cls._group.values():
                if re.match(name, node.name):
                    return node

    def __new__(cls, name=None, *args, **kwargs):
        existing_node = cls.find_node(name)
        if existing_node is not None:
            logger.info(f'Node "{name}" already exist, returning the existing one')
            return existing_node
        return super(Node, cls).__new__(cls)

    def __init__(self, name):
        self.name = name
        self.id = hex(id(self))
        self.__tasks = set()
        self.changed = asyncio.Event()
        self.create_task(self.__change_listener())

    def __str__(self):
        return f'node "{self.name}"'

    def _register(self):
        self._group[self.id] = self
        self.group_changed.set()
        self.group_changed.clear()

    def create_task(self, future):
        task = asyncio.create_task(future)
        self.__tasks.add(task)
        return task

    def Condition(self):
        cond = asyncio.Condition()
        self.create_task(self.__condition_listener(cond))
        return cond

    async def __change_listener(self):
        while True:
            await self.changed.wait()
            self.group_changed.set()
            self.group_changed.clear()

    async def __condition_listener(self, cond):
        while True:
            async with cond:
                await cond.wait()
                self.changed.set()
                self.changed.clear()

    def _log_debug(self, msg):
        self._logger.debug(f'{self}: {msg}')

    def _log_info(self, msg):
        self._logger.info(f'{self}: {msg}')

    def _log_warning(self, msg):
        self._logger.warning(f'{self}: {msg}')

    def _log_error(self, msg):
        self._logger.error(f'{self}: {msg}')

    def kill(self):
        print('kill')
