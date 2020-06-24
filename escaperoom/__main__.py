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
from sys import argv
import logging

logger = logging.getLogger(__name__)


def parse_args():

    from argparse import ArgumentParser

    parser = ArgumentParser(description='Escape room server')
    parser.add_argument('-v', '--verbose', action='store_true',
                        help='Print info log')
    parser.add_argument('-vv', '--debug', action='store_true',
                        help='Print debug log')
    parser.add_argument('--master', action='store_true',
                        help='Start server as the master node')
    return parser.parse_args()




def main():

    args = parse_args()

    from .misc.logutils import init_logging_system
    level = (args.debug and 'DEBUG') or (args.verbose and 'INFO') or 'WARNING'
    init_logging_system(level=level)

    if args.master:

        from .network.service import EscaperoomUnitService
        service = EscaperoomUnitService()
        service.start()

        loop = asyncio.get_event_loop()
        loop.run_until_complete(asyncio.sleep(100))

    else:

        from .network.service import EscaperoomUnitDiscovery
        discovery = EscaperoomUnitDiscovery()
        discovery.start()

        loop = asyncio.get_event_loop()
        loop.run_until_complete(asyncio.sleep(100))


if __name__ == '__main__':

    try:
        main()

    except KeyboardInterrupt:
        logger.warning('Keyboard interrupted')
