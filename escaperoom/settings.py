
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

from os.path import expanduser, join

testing = None 

com_debug = False 
log_debug = False 
misc_debug = False

escaperoom_dir = expanduser('~/Documents/EscapeRoom')

def read_config(path):
    print('execute settings')

read_config(expanduser('/etc/escaperoom'))
read_config(expanduser('~/.config/escaperoom'))

#TODO if not defined
rooms_dir = join(escaperoom_dir, 'rooms')
records_file = join(escaperoom_dir, 'games.db')
