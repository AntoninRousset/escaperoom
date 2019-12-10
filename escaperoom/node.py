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

import asyncio

def create_task(future):
    # python3.6
    loop = asyncio.get_event_loop()
    return loop.create_task(future)
    # python3.7
    #return asyncio.create_task(future)

#Abstract class
class Node():
    def __init__(self):
        self.__tasks = set()
        self.changed = asyncio.Event()

    def create_task(self, future):
        task = create_task(future)
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

