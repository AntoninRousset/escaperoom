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

from asyncio import *
from asyncio import subprocess

try:
    create_task
except NameError:
    def create_task(*args, **kwargs):
        return get_event_loop().create_task(*args, **kwargs)

def run_until_complete(*args, **kwargs):
    return get_event_loop().run_until_complete(*args, **kwargs)

def run_in_executor(*args, **kwargs):
    return get_event_loop().run_in_executor(*args, **kwargs)

async def ensure_finished(cr):
    if isfuture(cr) or iscoroutine(cr):
        return await cr
    else:
        return cr

#Bypass asyncio bug
async def wait_on_condition(condition: Condition, *, timeout=None):
    loop = get_event_loop()
    waiter = loop.create_future()

    def release_waiter(*_):
        if not waiter.done():
            waiter.set_result(None)

    if timeout is not None:
            timeout_handle = loop.call_later(timeout, release_waiter)
    wait_task = loop.create_task(condition.wait())
    wait_task.add_done_callback(release_waiter)

    try:
        await waiter
        if wait_task.done():
            return True
        else:
            raise TimeoutError()
    except (TimeoutError, CancelledError):
        wait_task.remove_done_callback(release_waiter)
        wait_task.cancel()
        await wait([wait_task])
        raise
    finally:
        if timeout is not None:
            timeout_handle.cancel()
