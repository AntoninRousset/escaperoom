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

from . import asyncio, config

ROOT = Path(os.path.dirname(__file__))

logger = logging.getLogger('escaperoom')

def get_args():
    parser = ArgumentParser(description='EscapeRoom server')
    parser.add_argument('--rooms', type=str, default='.*',
                        help='Regex of the rooms to load')
    return parser.parse_args()

def load_rooms(rooms_dir, rooms):
    @contextmanager
    def sibling_imports(module):
        old_module = sys.modules.get(module.__name__)
        sys.modules[module.__name__] = module
        try:
            yield
        finally:
            if old_module is None:
                sys.modules.pop(module.__name__)
            else:
                sys.modules[module.__name__] = old_module

    loader_details = (
        importlib.machinery.SourceFileLoader,
        importlib.machinery.SOURCE_SUFFIXES
        )
    room_finder = importlib.machinery.FileFinder(str(rooms_dir), loader_details)
    for child in Path(rooms_dir).iterdir():
        name = child.stem
        spec = room_finder.find_spec(name)
        if spec is None or spec.loader is None:
            logger.debug(f'skipping child "{name}" in {rooms_dir}')
            continue
        if name in rooms:
            raise Exception('duplicated room\'s names')
        room = importlib.util.module_from_spec(spec)
        logger.info(f'loading room: {name}')
        with sibling_imports(room):
            spec.loader.exec_module(room)

def main():
    args = get_args()
    load_rooms(Path(config['DEFAULT']['rooms_dir']).expanduser(), args.rooms)
    asyncio.get_event_loop().run_forever()

if __name__ == '__main__':
    main()
