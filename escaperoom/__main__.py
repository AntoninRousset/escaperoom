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

import errno, importlib, logging, os, re, subprocess, sys
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


async def _room_exectutor(pythonpath, room_name):
        room_env = os.environ.copy()
        room_env['PYTHONPATH'] = ':'.join(p for p in pythonpath if p)
        args = ['python', '-m', room_name]
        co = await asyncio.create_subprocess_exec(*args, env=room_env)
        await co.wait()

def launch_rooms(rooms_re):
    rooms_dir = Path(config['DEFAULT']['rooms_dir']).expanduser()
    rooms = set()
    for child in Path(rooms_dir).iterdir():
        room_name = child.stem
        if not re.match(rooms_re, room_name):
            continue
        if room_name in rooms:
            raise Exception('duplicated room\'s names "{room_name}"')
        pythonpath = [str(rooms_dir), str(ROOT.parent), *sys.path]
        logger.info(f'launching room: {room_name}') #TODO it doesnt do anything
        asyncio.create_task(_room_exectutor(pythonpath, room_name))
        rooms.add(room_name)

#TODO master server that redirect each request to the slave server

def main():
    args = get_args()
    rooms = launch_rooms('.*')
    loop()

if __name__ == '__main__':
    main()
