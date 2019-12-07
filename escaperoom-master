#!/usr/bin/env python3.6

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

import asyncio, sys
import argparse
from importlib import import_module

import escaperoom.settings
#settings.testing = 'b3'

async def main():
    parser = argparse.ArgumentParser(description='EscapeRoom server')
    parser.add_argument(
        '--host', type=str, default='0.0.0.0',
        help='Host for the HTTP server (default: 0.0.0.0)'
        )
    parser.add_argument(
        '--port', type=int, default=8080, help='Port for HTTP server (default: 8080)'
    )
    args = parser.parse_args()

    import escaperoom.server as server
    server.games['time'] = import_module('escaperoom.games.time').game
    await server.start(host=args.host, port=args.port)
    while True:
        await asyncio.sleep(3600)

import signal

def shutdown(loop, signal=None):
    if signal:
        print('shutdown signal')

def custom_exception_handler(loop, context):
    loop.default_exception_handler(context)
    exception = context.get('exception')
    print(context)

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    #for s in (signal.SIGHUP, signal.SIGTERM, signal.SIGINT):
    #    loop.add_signal_handler(s, shutdown(loop, signal=s))
    #loop.set_exception_handler(custom_exception_handler)
    loop.create_task(main())
    loop.run_forever()

