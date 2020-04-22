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

from sqlalchemy import Column, Integer, String, Boolean, DateTime
from .table import DataTable, DataRow


class GamesTable(DataTable):
    """
    Accessor for the games table.
    """

    def __new__(cls, db):

        return super().__new__(cls, 'games', db, GameData,

                               Column('game_id', Integer, primary_key=True),
                               Column('room_name', String),
                               Column('gamemaster_email', String),

                               Column('group_name', String),
                               Column('group_size', Integer),
                               Column('group_reason', Integer),
                               Column('leader_firstname', String),
                               Column('leader_lastname', String),
                               Column('leader_email', String),
                               Column('leader_postcode', Integer),

                               Column('test', Boolean),

                               Column('planned_date', DateTime),
                               Column('creation_date', DateTime),
                               Column('start_date', DateTime),
                               Column('end_date', DateTime),
                               Column('archiving_date', DateTime),

                               Column('comments', String),
                               )

    async def new(self, room, gamemaster):
        """
        Creates a new game in the table.

        Parameters
        ----------
        room: RoomData
            The room in which the game is played.
        gamemaster : GamemasterData
            The Gamemaster responsible for the game.

        Returns
        -------
        game : GameData
            The created game accessor.
        """

        from datetime import datetime

        for ref in (room, gamemaster):
            if not await ref.exists():
                raise ValueError(f'{ref} does not exists')

        return await super().new(room_name=room.room_name,
                                 gamemaster_email=gamemaster.gamemaster_email,
                                 creation_date=datetime.now())


class GameData(DataRow):
    """
    Accessor for a game.
    """

    def __init__(self, game_id, games_table):
        """
        Parameters
        ----------
        games_table: GamesTable
            Key for the game row. If a GameData is given, the latter is copied
            and games_table can be omitted.
        games_table : GamesTable
            Accessor to the games table. Can be ommited if game_id is a
            GameData.
        """

        super().__init__(game_id, games_table)

    @property
    def game_id(self):
        return self.key[0]

    async def get_room(self):
        """
        Get the room in which the game is played.

        Returns
        -------
        room: RoomData
            Accessor the room in which the game is played.
        """
        return self.db.rooms[await self.get('room_name')]

    async def get_gamemaster(self):
        """
        Get the gamemaster responsible of this game.

        Returns
        -------
        gamemaster: GamemasterData
            Accessor the gamemaster responsible of this game.
        """
        return self.db.gamemasters[await self.get('gamemaster_email')]

    async def new_clue(self, content):
        """
        Create a new clue in this game.

        Returns
        -------
        content: str
            The clue message.

        Returns
        -------
        clue: ClueData
            An accessor to the newly created clue.
        """
        return await self.db.clues.new(game=self, content=content)
