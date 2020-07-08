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

from aiohttp import web
from os.path import dirname
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


class HTTPServer:

    ROOT = Path(dirname(__file__)) / 'html'

    def __init__(self, context):

        from .handler import MainHandler

        self.app = MainHandler(self.ROOT, context)
        self.site = None

    async def start(self, host='0.0.0.0', port=8080):
        runner = web.AppRunner(self.app)
        await runner.setup()
        self.site = web.TCPSite(runner, host, port)
        await self.site.start()
        logger.info(str(self))

    def __str__(self):
        if not self.site:
            return f'HTTP server, not running'
        return f'HTTP server running on {self.site._host}:{self.site._port}'
