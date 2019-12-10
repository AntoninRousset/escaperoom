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

from configparser import ConfigParser
from pathlib import Path
from os.path import dirname

config = ConfigParser()
ROOT = dirname(__file__)
config.read(Path(f'{ROOT}/escaperoom.conf').resolve())
config.read(config['DEFAULT'].get('conf_file'))

from .game import Game
from .logic import Logic, Puzzle
from .misc import Misc, LocalCamera, Display
from .network import Network, Bus, Device, Attribute

