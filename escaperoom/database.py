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
from datetime import datetime
from pathlib import Path

from . import config

#TODO per room database
connection = sqlite3.connect(str(Path(config['DEFAULT']['games_file']).expanduser()))
with connection:
    connection.execute(
    '''CREATE TABLE IF NOT EXISTS games (
        id integer PRIMARY KEY,
        name text NOT NULL,
        status text NOT NULL,
        n_player integer NOT NULL,
        timeout_enabled boolean NOT NULL,
        timeout timestamp,
        start_time timestamp,
        end_time timestamp)''')

def new_game(name, options):
    with connection:
        cursor = connection.cursor()
        cursor.execute(
        '''INSERT INTO games (name, status, n_player, timeout_enabled, timeout)
        VALUES (?, ?, ?, ?, ?)''', (name, options['status'], options['n_player'], options['timeout_enabled'], options['timeout']))
        return cursor.lastrowid

def game_start(game_id, start_time):
    with connection:
        connection.execute(
        '''UPDATE games SET start_time=? WHERE id=?''', (start_time, game_id))

def game_end(game_id, end_time):
    with connection:
        connection.execute(
        '''UPDATE games SET end_time=? WHERE id=?''', (end_time, game_id))
