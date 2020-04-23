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
from sqlalchemy import Column, Integer, DateTime, String
from .room import RoomData
from .game import GameData
from .gamemaster import GamemasterData


class CluesTable(DataTable):
    """
    Accessor for the clues table.
    """

    def __new__(cls, db, *args, **kwargs):
        return super().__new__(cls, 'clues', db, ClueData,
                               Column('clue_id', Integer, primary_key=True),
                               Column('game_id', Integer),
                               Column('date', DateTime),
                               Column('content', String),
                               )

    async def new(self, game, content):
        """
        Creates a new clues in the table.

        The clue creation date is set once this function is called.

            Parameters
            ----------
            game : game_id or GameData
                The game in which the clue is emitted.
            content: str
                Clue message.

            Returns
            -------
            clue : ClueData
                The created clue accessor.
        """

        from datetime import datetime

        if not await game.exists():
            raise ValueError(f'{game} does not exists')

        return await super().new(game_id=game.game_id,
                                 date=datetime.now(),
                                 content=content)

    async def get_most_frequent(self, limit=None, room=None, game=None,
                                gamemaster=None):
        """
        Get the most frequent clues.

        The result is sorted by decreasing frequency and the clues a grouped
        based on the clue content.

        Parameters
        ----------
        limit : None or integer
            Limit the number of results. The length of the list will be less
            or equal to limit. If None, its length will be equal to the ammount
            of distinct clue content.
        room : None, RoomData or iterable of RoomData
            If set, filter the clues to the given room(s).
        game : None, GameData or iterable of GameData
            If set, filter the clues to the given game(s).
        gamemaster : None, GamemasterData or iterable of GamemasterData
            If set, filter the clues to the given gamemaster(s).

        Returns
        -------
        nb, clue, content : list(tuple(int, ClueData, str))
            A list of tuples containing the number of occurences, the clue
            accessor and its content.
        """

        from sqlalchemy import desc, func, select

        # count nb of occurences
        query = select([func.count(self.db.clues.c.content).label('nb'),
                        self.db.clues.c.clue_id,
                        self.db.clues.c.content])

        # filter game
        if game is not None:
            game = {game} if isinstance(game, GameData) else game
            game_id = {g.game_id for g in game}
            query = query.where(self.c.game_id.in_(game_id))

        # filter room
        if room is not None:
            room = {room} if isinstance(room, RoomData) else room
            game_id = [g.game_id for r in set(room)
                       for g in await r.get_games()]
            query = query.where(self.c.game_id.in_(game_id))

        # filter gamemaster
        if gamemaster is not None:
            if isinstance(gamemaster, GamemasterData):
                gamemaster = {gamemaster}
            game_id = [g.game_id for gm in set(gamemaster)
                       for g in await gm.get_games()]
            query = query.where(self.c.game_id.in_(game_id))

        # grouping and ordering
        query = query.group_by(self.db.clues.c.content)
        query = query.order_by(desc('nb'))

        # limit number of results
        if limit is not None:
            query = query.limit(limit)

        # wrap clue_id into ClueData
        return [(n, self.db.clues[clue_id], content)
                async for n, clue_id, content in self.db.iterate(query)]


class ClueData(DataRow):

    def __init__(self, clue_id, clues_table=None):
        """
        Accessor for a clue.

        Parameters
        ----------
        clue_id : integer or ClueData
            Key for the clue row. If a ClueData is given, the latter is copied
            and clues_table can be omitted.
        clues_table : CluesTable
            Accessor to the clues table. Can be ommited if clue_id is a
            ClueData.
        """

        super().__init__(clue_id, clues_table)

    @property
    def clue_id(self):
        return self.key[0]

    async def get_game(self):
        """
        Get the game in which the clue has been emitted.

        Returns
        -------
        game: GameData
            The game in which the clue has been emitted.
        """
        return self.db.games[await self.get('game_id')]
