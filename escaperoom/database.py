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

import sqlite3

import settings

connection = sqlite3.connect(settings.records_dir+'games.db')
with connection:
    connection.execute('''
    CREATE TABLE IF NOT EXISTS games (
        id integer PRIMARY KEY,
        room_name text NOT NULL,
        status text NOT NULL,
        start_time timestamp,
        end_time timestamp)'''
        )


def write_game(game, new=False):
    with connection:
        connection.execute('INSERT INTO games VALUES (?, ?, ?, ?)',
                (1, game.name, 'testing', game.start_time, game.end_time))
        #TODO how to increment ID?
    return 1 #TODO id


