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

import configparser, os.path
from pathlib import Path

#TODO All config should be red in config.py
config = configparser.ConfigParser()
ROOT = Path(os.path.dirname(__file__))
config.read(Path(ROOT/'escaperoom.conf').resolve(), encoding='utf-8')

for path in config['DEFAULT']['escaperoom_dir'], config['DEFAULT']['rooms_dir']:
    try:
        Path(path).expanduser().mkdir(parents=True, exist_ok=True)
    except FileExistsError:
        pass

config.read(Path(config['DEFAULT']['conf_file']).expanduser(), encoding='utf-8')

from .logging import ColoredFormatter

import logging.config
logging.config.fileConfig(config) #TODO per room logging

from .game import Game
from .logic import Action, action, Condition, condition
from .misc import LocalCamera, RemoteCamera, LocalCluesDisplay, RemoteCluesDisplay, Chronometer
from .media import Audio
from .network import SerialBus, Device, device, SerialDevice
from .server import HTTPServer

def loop():
    asyncio.get_event_loop().run_forever()
