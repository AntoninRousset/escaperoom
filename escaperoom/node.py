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

#Abstract class
class Node():
    def __init__(self):
        self.__tasks = set()
        self.changed = asyncio.Event()

    def create_task(self, future):
        task = asyncio.create_task(future)
        self.__tasks.add(task)
        return task

    def Condition(self):
        cond = asyncio.Condition()
        self.create_task(self.__condition_listener(cond))
        return cond

    async def __condition_listener(self, cond):
        while True:
            async with cond:
                await cond.wait()
                self.changed.set()
                self.changed.clear()

    def kill(self):
        print('kill')

