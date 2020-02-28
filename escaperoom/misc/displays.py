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

from asyncio.subprocess import PIPE
from copy import copy
import aiohttp, json, re
from abc import ABC, abstractmethod

from . import asyncio, Misc
from ..subprocess import SubProcess


class Display(Misc):
    pass


class CluesDisplay(Display):

    def __init__(self, name, game=None):
        super().__init__(name)
        self.name = name
        if game is not None:
            self.game = game
            self.create_task(self._chronometer_listener())

    def __str__(self):
        return f'display "{self.name}"'

    async def _chronometer_listener(self):
        while True:
            async with self.game.desc_changed:
                runn = self.game.start_time is not None \
                    and self.game.end_time is None
                seconds = self.game.chronometer.total_seconds()
                self.create_task(self.set_chronometer(runn, seconds))
                await self.game.desc_changed.wait()


class LocalCluesDisplay(CluesDisplay):

    EXEC_ARGS = ['escaperoom_cluesdisplay']

    def __init__(self, name, game=None, **kwargs):
        super().__init__(name, game)
        self.start_display(**kwargs)

    def start_display(self, power=True, color='green'):
        args = copy(self.EXEC_ARGS)
        if not power:
            args.append('--poweroff')
        args.append('--color='+color)
        self.sp = SubProcess(self.name, *self.EXEC_ARGS, stdin=PIPE)

    async def _write_to_process(self, data):
        try:
            self.sp.stdin.write(data)
            await self.sp.stdin.drain()
        except AttributeError:
            await asyncio.sleep(1)
            await self._write_to_process(data)
        except Exception as e:
            self._log_error(f'{self} is dead: {e}')
            raise RuntimeError()

    async def set_layout(self, layout):
        msg = 'layout ' + ' '.join(layout) + '\n'
        await self._write_to_process(msg.encode())

    async def set_msg_alignment(self, alignment):
        msg = f'alignment {alignment}\n'
        await self._write_to_process(msg.encode())

    async def set_text_color(self, color):
        msg = f'color {color}\n'
        await self._write_to_process(msg.encode())

    async def set_msg(self, msg):
        msg = msg.replace('\n', '\\n')
        msg = f'clue {msg}\n'
        await self._write_to_process(msg.encode())

    async def set_timer(self, speed, seconds):
        msg = f'timer {float(speed)} {seconds}\n'
        await self._write_to_process(msg.encode())

    async def set_image(self, image):
        msg = f'image {image}\n'
        await self._write_to_process(msg.encode())

    async def set_background(self, bg):
        msg = f'background {bg}\n'
        await self._write_to_process(msg.encode())

    async def set_power(self, state):
        msg = f'power {"on" if state else "off"}\n'
        await self._write_to_process(msg.encode())


class RemoteCluesDisplay(CluesDisplay):

    def __init__(self, name, address, game=None, *, rename=None):
        if rename is None:
            rename = name
        super().__init__(rename, game)
        self.address = address
        self.remote_name = name

    async def set_chronometer(self, running, seconds):
        data = {'type': 'chronometer', 'running': running, 'seconds': seconds}
        await self._send(data)

    async def set_msg(self, msg):
        await self._send({'type': 'msg', 'msg': msg})

    async def set_img(self, img):
        await self._send({'type': 'image', 'image': str(img)})

    async def _send(self, data):
        try:
            async with aiohttp.ClientSession() as s:
                address = self.address + f'/display?name={self.remote_name}'
                async with s.post(address, data=json.dumps(data)) as r:
                    return await r.json()
        except aiohttp.ClientError as e:
            self._log_warning(f'error while connecting to camera on {self.address}')
            #TODO? retry with "sending" lock?

