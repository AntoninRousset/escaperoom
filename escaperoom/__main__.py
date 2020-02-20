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

import errno, importlib, logging, os, re, sys
from argparse import ArgumentParser
from contextlib import contextmanager
from pathlib import Path

from . import asyncio, config, loop

ROOT = Path(os.path.dirname(__file__))

logger = logging.getLogger('escaperoom')


def get_args():
    parser = ArgumentParser(description='EscapeRoom server')
    parser.add_argument('--rooms', type=str, default='.*',
                        help='Regex of the rooms to load')
    return parser.parse_args()


def launch_rooms(rooms_re):
    rooms_dir = Path(config['DEFAULT']['rooms_dir']).expanduser()
    rooms = set()
    for child in Path(rooms_dir).iterdir():
        room_name = child.stem
        if not re.match(rooms_re, room_name):
            continue
        if room_name in rooms:
            raise Exception('duplicated room\'s names "{room_name}"')
        path = rooms_dir/child
        co = asyncio.create_subprocess_shell(
                f'python "{path}"', env={'PYTHONPATH' : ROOT.parent}
                )
        logger.info(f'launching room: {room_name}')
        asyncio.run_until_complete(co)
        rooms.add(room_name)

def main():
    args = get_args()
    rooms = launch_rooms('.*')
    loop()

if __name__ == '__main__':
    main()
