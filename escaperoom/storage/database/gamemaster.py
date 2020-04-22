#!/usr/bin/env python
# -*- coding: utf-8 -*-

from .table import DataTable, DataRow
from sqlalchemy import Column, String, select


class GamemastersTable(DataTable):

    def __new__(cls, db, *args, **kwargs):
        """
        Accessor for the gamemasters table.
        """
        return super().__new__(cls, 'gamemasters', db, GamemasterData,
                               Column('email', String, primary_key=True),
                               Column('firstname', String),
                               Column('lastname', String),
                               )

    async def new(self, email, firstname, lastname):
        """
        Creates a new gamemaster in the table.

        Parameters
        ----------
        firstname : str
            The first name of the gamemaster.
        lastname : str
            The last name of the gamemaster.
        email : str
            The email adress of the gamemaster.

        Returns
        -------
        gamemaster: GamemasterData
            The created gamemaster accessor.
        """
        return await super().new(email=email,
                                 firstname=firstname,
                                 lastname=lastname,
                                 )

    async def get_all(self):
        """
        Get all informations about all gamemasters.

        Returns
        -------
        gamemasters : dict email -> dict('email', firstname', 'lastname')
            All gamemasters informations
        """

        query = self.db.gamemasters.select()

        def pack(email, firstname, lastname):
            return {
                'email': email,
                'firstname': firstname,
                'lastname': lastname,
            }

        return {info[0]: pack(*info) async for info in self.db.iterate(query)}


class GamemasterData(DataRow):

    def __init__(self, gamemaster_id, gamemasters_table=None):
        """
        Accessor for a gamemaster.

        Parameters
        ----------
        gamemaster_id : integer or GamemasterData
            Key for the gamemaster row. If a GamemasterData is given, the
            latter is copied and gamemasters_table can be omitted.
        gamemasters_table : GamemastersTable
            Accessor to the gamemasters table. Can be ommited if gamemaster_id
            is a GamemasterData.
        """

        super().__init__(gamemaster_id, gamemasters_table)

    @property
    def gamemaster_id(self):
        return self.key[0]

    async def get_games(self):
        """
        Get the games supervised by this gamemaster.

        Returns
        -------
        games : list of GameData
            A list of gamed supervised by this gamemaster.
        """

        games = self.db.games
        cond = games.c['gamemaster_id'] == self.gamemaster_id
        query = select([games.c['game_id']]).where(cond)

        return [self.db.games[game_id]
                async for (game_id,) in self.db.iterate(query)]
