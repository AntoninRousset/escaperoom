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
from datetime import datetime, timedelta

from . import Misc


class Chronometer(Misc):

    _group = Misc.Group()

    def __init__(self, name='__main'):
        super().__init__(name)
        if self._first_init:
            self.start_time = None #TODO list of plays and pauses
            self.end_time = None

    def start(self):
        self.start_time = datetime.today()

    def stop(self):
        self.end_time = datetime.today()

    def elapsed(self):
        if self.start_time is None:
            return timedelta(0)
        elif self.end_time is None:
            return datetime.today() - self.start_time
        elif self.end_time > self.start_time:
            return self.end_time - self.start_time
        else:
            raise RuntimeError()

    def is_running(self):
        return self.start_time is not None and self.end_time is None


