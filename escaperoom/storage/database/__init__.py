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

import databases as db
import sqlalchemy as sql
import logging

from .room import RoomsTable
from .game import GamesTable
from .gamemaster import GamemastersTable
from .clues import CluesTable


class Database(db.Database):

    def __init__(self, hostname, backend='sqlite'):

        url = f'{backend}://{hostname}'

        self.logger = logging.getLogger('escaperoom.storage.data.database')

        # TODO: implement state_transitions table?
        # self.state_transitions = StateTransitionsTable(self.metadata)

        self.metadata = sql.MetaData()
        self.metadata.create_all(bind=sql.create_engine(url))
        super().__init__(url)
        self.logger.debug(f'Database loaded at {self.url}')

        self.rooms = RoomsTable(self)
        self.games = GamesTable(self)
        self.gamemasters = GamemastersTable(self)
        self.clues = CluesTable(self)

