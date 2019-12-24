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

import errno, importlib.util, sys
from argparse import ArgumentParser
from pathlib import Path

from . import asyncio, config, server

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

def get_rooms(rooms_dir):
    sys.path.append(str(rooms_dir))
    rooms = dict()
    for child in Path(rooms_dir).iterdir():
        name = child.stem
        if name in rooms:
            raise Exception('duplicated room\'s names')
        path = Path(rooms_dir) / child
        spec = importlib.util.spec_from_file_location(name, path) 
        try:
            if spec is None:
                path /= '__init__.py'
                spec = importlib.util.spec_from_file_location(name, path) 
            if spec is not None:
                room = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(room)
                rooms[name] = room.game
        except FileNotFoundError:
            pass
    sys.path.pop()
    return rooms

def main():
    args = get_args()
    server.games.update(get_rooms(Path(config['DEFAULT']['rooms_dir']).expanduser()))
    asyncio.get_event_loop().create_task(server.start(host=args.host, port=args.port))
    asyncio.get_event_loop().run_forever()

if __name__ == '__main__':
    main()
