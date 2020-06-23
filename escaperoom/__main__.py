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

import asyncio


def main():

    from .misc.logutils import init_logging_system
    init_logging_system(level='WARNING')

    loop = asyncio.get_event_loop()
    loop.run_until_complete(asyncio.sleep(2))


if __name__ == '__main__':
    main()
