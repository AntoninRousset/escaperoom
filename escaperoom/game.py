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

from . import asyncio, database
from .misc import Chronometer

from datetime import datetime, timedelta

class Game(ABC):

    name = None
    default_options = {
            'status' : 'official',
            'n_player' : 4,
            'timeout_enabled' : True,
            'timeout' : '01:00:00'
        }
    changed = asyncio.Condition()
    _chronometer = Chronometer('__game')

    @classmethod
    async def start(cls, options):
        cls._chronometer.start()

    @classmethod
    async def stop(cls, options):
        cls._chronometer.stop()

    @classmethod
    def is_running(cls):
        return cls._chronometer.is_running()
