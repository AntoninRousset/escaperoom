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

import errno, importlib.util, logging, os, re, sys
from argparse import ArgumentParser
from pathlib import Path

from . import asyncio, config

ROOT = Path(os.path.dirname(__file__))

logger = logging.getLogger('escaperoom')

def get_args():
    parser = ArgumentParser(description='EscapeRoom server')
    parser.add_argument('--rooms', type=str, default='.*',
                        help='Regex of the rooms to load')
    return parser.parse_args()

def load_rooms(rooms_dir, rooms):
    try:
        os.remove(ROOT/'rooms')
    except FileNotFoundError:
        pass
    os.symlink(rooms_dir, ROOT/'rooms', target_is_directory=True)
    for child in Path(rooms_dir).iterdir():
        name = child.stem
        if name == '__pycache__' or not re.match(rooms, name):
            continue
        if name in rooms:
            raise Exception('duplicated room\'s names')
        logger.info(f'loading room: {name}')
        importlib.import_module(f'.rooms.{name}', 'escaperoom')

def main():
    args = get_args()
    load_rooms(Path(config['DEFAULT']['rooms_dir']).expanduser(), args.rooms)
    asyncio.get_event_loop().run_forever()

if __name__ == '__main__':
    main()
