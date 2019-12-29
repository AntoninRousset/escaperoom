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

from abc import ABC
from collections import defaultdict

from . import asyncio

class ANode(ABC):

    class Changed():

        @classmethod
        def cond_factory(cls):
            return asyncio.Condition()

        def __init__(self, node, conds=None, attrs=None):
            super().__init__()
            if conds is None:
                conds = defaultdict(self.cond_factory)
            self._node = node
            self._conds = conds
            self._attrs = attrs

        def __call__(self, *attrs):
            if self._attrs is not None:
                attrs &= self._attrs
            return Changed(self._node, self._conds, attrs)

        async def __aenter__(self):
            await self._master_cond.__aenter__()
            if self._attrs is None:
                cs = (c.__aenter__() for c in self.__conds.values())
                await asyncio.gather(*cs)
            else:
                cs = (self._conds[attr].__aenter__() for attr in self._attrs)
                await asyncio.gather(*cs)
                await self._master_cond.__aexit__()

        async def __aexit__(self, *ar, **kw):
            if self._attrs is None:
                cs = (c.__aexit__(*ar, **kw) for c in self.__conds.values())
                await asyncio.gather(*cs)
                await self._master_cond.__aexit__(*ar, **kw)
            else:
                cs = (self._conds[attr].__aexit__(*ar, **kw) for attr in self._attrs)
                await asyncio.gather(*cs)

        def __aiter__(self):
            return self

        async def __anext__(self):
            while True:
                async with self:
                    yield (self._node.__getattribute__(attr) for attr in self.attrs)
                    await self.wait()

        async def wait():
            if self._attrs is None:
                await self._master_cond.wait()
            else:
                conds = {self._conds[attr] for attr in self._attrs}
                ts = {asyncio.create_task(cond.wait()) for cond in conds}
                await asyncio.wait(ts, return_when=asyncio.FIRST_COMPLETED)
                cs = {cond.acquire() for cond in conds if not cond.locked()}
                await asyncio.gather(*cs)

        def notify_all():
            self._master_cond.notify_all()
            if self._attrs is not None:
                conds = {self._conds[attr] for attr in self._attrs}
                cs = {cond.notify_all() for cond in conds}
                await asyncio.gather(*cs)

        @property
        def _master_cond(self):
            return self._conds[None]

    def __init__(self):
        self.__tasks = set()
        self.changed = ANode.Changed(self, self.__conds)

    def create_task(self, future):
        task = asyncio.create_task(future)
        self.__tasks.add(task)
        return task

    def kill(self):
        print('kill')

