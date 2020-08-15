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
import logging


logger = logging.getLogger(__name__)


def parse_args():

    from argparse import ArgumentParser

    parser = ArgumentParser(description='Escape room server')
    parser.add_argument('-v', '--verbose', action='store_true',
                        help='print info log')
    parser.add_argument('-vv', '--debug', action='store_true',
                        help='print debug log')
    parser.add_argument('--http-server', action='store_true',
                        help='start http server')
    parser.add_argument('--clusters-urls', action='store', required=True,
                        help='list of etcd servers to connect to')
    parser.add_argument('--member-name', action='store', required=True,
                        help='name for connection to the cluster')
    return parser.parse_args()


async def init(args):

    from .shared.cluster import Cluster

    for endpoint in args.clusters_urls.split(','):
        cluster = Cluster(endpoint, persistent=True)  # TODO Check duplicates
        asyncio.create_task(cluster.start())

    if args.http_server:
        asyncio.create_task(run_http_server())


def main():

    from .misc.logutils import init_logging_system

    args = parse_args()

    level = (args.debug and 'DEBUG') or (args.verbose and 'INFO') or 'WARNING'
    init_logging_system(level=level)

    try:
        loop = asyncio.get_event_loop()
        loop.run_until_complete(init(args))
        loop.run_forever()

    except KeyboardInterrupt:
        logger.warning('Keyboard interrupted')


async def run_http_server():

    from .context import EscaperoomContext
    from .server import HTTPServer

    print('*****')

    async with EscaperoomContext() as context:
        async with HTTPServer(context):
            await context.quit_event.wait()


if __name__ == '__main__':
    main()
