
#!/usr/bin/env python

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

from pathlib import Path

testing = None 

com_debug = False 
log_debug = False 
misc_debug = False

escaperoom_dir = Path('~/Documents/EscapeRoom').expanduser()
rooms_dir = None
records_file = None

def read_config(path):
    print('TODO read config')

read_config('/etc/escaperoom')
read_config(Path('~/.config/escaperoom').expanduser())


if rooms_dir is None:
    rooms_dir = escaperoom_dir/'rooms'
if records_file is None:
    records_file = escaperoom_dir/'games.db'
