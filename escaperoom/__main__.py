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

import asyncio, errno, importlib.util, sys
from argparse import ArgumentParser
from pathlib import Path

from . import settings, server

def get_args():
    parser = ArgumentParser(description='EscapeRoom server')
    parser.add_argument(
        '--host', type=str, default='0.0.0.0',
        help='Host for the HTTP server (default: 0.0.0.0)'
        )
    parser.add_argument(
        '--port', type=int, default=8080, help='Port for HTTP server (default: 8080)'
    )
    return parser.parse_args()

def create_dirs():
    for path in settings.escaperoom_dir, settings.rooms_dir:
        try:
            Path(path).mkdir(exist_ok=True)
        except FileExistsError:
            pass

def get_rooms(rooms_dir):
    try:
        Path(rooms_dir).mkdir(exist_ok=True)
    except FileExistsError:
        pass
    #sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
    rooms = dict()
    for child in Path(rooms_dir).iterdir():
        name = child.stem
        if name in rooms:
            raise Exception('duplicated room\'s names')
        spec = importlib.util.spec_from_file_location(name, Path(rooms_dir) / child)
        if spec is not None:
            room = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(room)
            rooms[name] = room.game
    return rooms

print(f'name: {__name__}')
if __name__ == '__main__':
    args = get_args()
    create_dirs()
    server.games.update(get_rooms(settings.rooms_dir))
    server.start(host=args.host, port=args.port)
    asyncio.get_event_loop().run_forever()

