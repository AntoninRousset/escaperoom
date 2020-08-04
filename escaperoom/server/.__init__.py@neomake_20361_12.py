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


LOGGER = logging.getLogger(__name__)


class HTTPServer:

    ROOT = Path(dirname(__file__)) / 'html'

    def __init__(self, context, host='0.0.0.0', port=8080):

        from .handler import MainHandler

        self.context = context
        self.host = host
        self.port = port
        self.main_handler = MainHandler(context, self.ROOT,)
        self.site = None
        self.runner = web.AppRunner(self.main_handler.app)

    async def start(self):
        await self.runner.setup()
        self.site = web.TCPSite(self.runner, self.host, self.port)
        await self.site.start()
        LOGGER.info(str(self))

    async def stop(self):
        await self.runner.cleanup()
        self.site = None

    async def __aenter__(self):
        await self.start()

    async def __aexit__(self, exc_type, exc, tb):
        await self.stop()

    def __str__(self):
        if not self.site:
            return f'HTTP server, not running'
        return f'HTTP server running on {self.site._host}:{self.site._port}'
