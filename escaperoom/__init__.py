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

import configparser, os, os.path
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
from .misc import Camera, LocalCamera, RemoteCamera, LocalCluesDisplay, RemoteCluesDisplay, Chronometer, Timer
from .media import Audio
from .network import SerialBus, Device, device, SerialDevice
from .server import HTTPServer
from .subprocess import SubProcess 

def loop():
    loop = asyncio.get_event_loop()
    try:
        loop.run_forever()
    finally:
        loop.run_until_complete(loop.shutdown_asyncgens())
        loop.close()

def clean_up():
    asyncio.run_until_complete(Camera.close_all())
    asyncio.run_until_complete(SubProcess.terminate_all())

import atexit
atexit.register(clean_up)

__all__ = ['Action', 'action', 'Condition', 'condition', 'Camera', 'asyncio',
           'LocalCamera', 'RemoteCamera', 'LocalCluesDisplay', 'Game', 'loop',
           'RemoteCluesDisplay', 'Chronometer', 'Audio', 'SerialBus', 'Device',
           'device', 'SerialDevice', 'HTTPServer', 'SubProcess', 'Timer']
