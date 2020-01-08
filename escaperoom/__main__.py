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

import errno, importlib.util, os, sys
from argparse import ArgumentParser
from pathlib import Path

from . import asyncio, config

ROOT = Path(os.path.dirname(__file__))

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

def load_rooms(rooms_dir):
    try:
        os.remove(ROOT/'rooms')
    except FileNotFoundError:
        pass
    os.symlink(rooms_dir, ROOT/'rooms', target_is_directory=True)
    rooms = set()
    for child in Path(rooms_dir).iterdir():
        name = child.stem
        if name == '__pycache__':
            continue
        elif name in rooms:
            raise Exception('duplicated room\'s names')
        room = importlib.import_module(f'.rooms.{name}', 'escaperoom')

def main():
    args = get_args()
    from .game import Game
    load_rooms(Path(config['DEFAULT']['rooms_dir']).expanduser())
    from . import server
    server.games.update(Game.games)
    asyncio.get_event_loop().create_task(server.start(host=args.host, port=args.port))
    asyncio.get_event_loop().run_forever()

if __name__ == '__main__':
    main()
