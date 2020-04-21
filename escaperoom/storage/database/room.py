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

from .table import DataTable, DataRow
from sqlalchemy import Column, Integer, String, Date, Interval, select
from .gamemaster import GamemasterData


class RoomsTable(DataTable):
    """
    Accessor for the rooms table.
    """

    def __new__(cls, db):
        return super().__new__(cls, 'rooms', db, RoomData,
                               Column('room_id', Integer, primary_key=True),
                               Column('name', String),
                               Column('opening_date', Date),
                               Column('max_nb_players', Integer),
                               Column('duration', Interval),
                               )

    async def new(self, name, opening_date, max_nb_players, duration):
        """
        Creates a new room in the table.

        Parameters
        ----------
        name : str
            Room name.
        opening_date : datetime.date
            Official opening date.
        max_nb_players : integer
            Maximum number of players allowed for a game in this room.
        duration : datetime.timedelta
            Official maximal game duration in this room.

        Returns
        -------
        game : GameData
            The created game accessor.
        """
        return await super().new(name=name,
                                 opening_date=opening_date,
                                 max_nb_players=max_nb_players,
                                 duration=duration)


class RoomData(DataRow):
    """
    Accessor for a room.
    """

    def __init__(self, room_id, rooms_table=None):
        """
        Parameters
        ----------
        room_id : integer or RoomData
            Key for the room row. If a RoomData is given, the latter is copied
            and rooms_table can be omitted.
        rooms_table : RoomsTable
            Accessor to the rooms table. Can be ommited if room_id is a
            RoomData.
        """

        super().__init__(room_id, rooms_table)

    @property
    def room_id(self):
        return self.key[0]

    async def new_game(self, gamemaster):
        """
        Create a new game in this room.

        Parameter
        ---------
        gamemaster : GamemasterData
            The gamemaster responsible for the new game.

        Returns
        -------
        game : GameData
            The created game.
        """
        return await self.db.games.new(room=self, gamemaster=gamemaster)

    async def get_games(self, gamemaster=None):
        """
        Get a list of the games played in this room.

        Parameters
        ----------
        gamemaster : None, GamemasterData or iterable of GamemasterData
            If set, filter the games suppervised by the given gamemaster(s).

        Returns
        -------
        game : list
            A list of games played in this room.
        """

        games = self.db.games
        cond = games.c['room_id'] == self.room_id
        query = select([games.c['game_id']]).where(cond)

        if gamemaster is not None:
            if isinstance(gamemaster, GamemasterData):
                gamemaster = {gamemaster}
            gamemaster_id = {gm.gamemaster_id for gm in gamemaster}
            query = query.where(games.c.gamemaster_id.in_(gamemaster_id))

        return [self.db.games[game_id]
                async for (game_id,) in self.db.iterate(query)]

    async def get_most_frequent_clues(self, limit=None, *args, **kwargs):
        """
        Get the most frequent clues emitted in this room.

        The result is sorted by decreasing frequency and the clues a grouped
        based on the clue content.

        Parameters
        ----------
        c.f. CluesTable.get_most_frequent()

        Returns
        -------
        nb, clue, content : list(tuple(int, ClueData, str))
            A list of tuples containing the number of occurences, the clue
            accessor and its content.
        """
        return await self.db.clues.get_most_frequent(limit, self, *args,
                                                     **kwargs)
