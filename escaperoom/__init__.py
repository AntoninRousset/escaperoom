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

from . import storage

import logging
from .logging import ColoredFormatter
from .game import Game
from .logic import Action, action, Condition, condition
from .misc import Camera, LocalCamera, RemoteCamera, LocalCluesDisplay, \
    RemoteCluesDisplay, Chronometer, Timer
from .media import Audio
from .network import SerialBus, Device, device, SerialDevice
from .registered import Registered
from .server import HTTPServer
from .subprocess import SubProcess

import logging.config
# TODO per room logging
logging.config.fileConfig(storage.config)


def loop(*, debug=False):
    loop = asyncio.get_event_loop()
    try:
        loop.set_debug(debug)
        loop.run_forever()
    except KeyboardInterrupt:
        print('Keyboard interrupt')
    finally:
        try:
            print('Attempting graceful shutdown', flush=True)
            entries = asyncio.wait({e.close() for e in Registered.entries()})
            loop.run_until_complete(entries)

            tasks = asyncio.gather(*asyncio.Task.all_tasks(loop),
                                   return_exceptions=True)
            import contextlib
            with contextlib.suppress(asyncio.CancelledError):
                tasks.cancel()
                loop.run_until_complete(tasks)
            loop.run_until_complete(loop.shutdown_asyncgens())
        except Exception as e:
            print('Graceful shutdown failed:', e.__repr__())
            print('Hard shutdown')
        finally:
            loop.close()


async def clean_up():

    await SubProcess.terminate_all()

__all__ = ['Action', 'action', 'Condition', 'condition', 'Camera', 'asyncio',
           'LocalCamera', 'RemoteCamera', 'LocalCluesDisplay', 'Game', 'loop',
           'RemoteCluesDisplay', 'Chronometer', 'Audio', 'SerialBus', 'Device',
           'device', 'SerialDevice', 'HTTPServer', 'SubProcess', 'Timer']
