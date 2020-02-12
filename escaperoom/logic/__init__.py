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

from abc import ABC, abstractmethod

from .. import asyncio, logging
from ..node import Node

logger = logging.getLogger('escaperoom.logic')

class Logic(Node):
    
    _logger = logger


class BoolLogic(Logic, ABC):

    @abstractmethod
    def __bool__(self):
        pass


from .actions import Action, action
from .conditions import Condition, condition
from .puzzles import Puzzle
