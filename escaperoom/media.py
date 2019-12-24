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

from aiortc.contrib.media import MediaPlayer, PlayerStreamTrack

from . import asyncio

__old_init = PlayerStreamTrack.__init__
def __init(self, *args, **kwargs):
    __old_init(self, *args, **kwargs)
    self.__frame = None
    self.frame_changed = asyncio.Lock()

__old_recv = PlayerStreamTrack.recv
async def __recv(self): 
    async with self.frame_changed:
        if self.__frame is None:
            frame = await __old_recv(self)
        else:
            frame = self.__frame
            self.__frame = None
    return frame

async def __get_frame(self, rgb=True):
    self.__frame = await __old_recv(self)
    if rgb and not self.__frame.format.is_rgb:
        self.__frame = self.__frame.to_rgb()
    return self.__frame

PlayerStreamTrack.__init__ = __init
PlayerStreamTrack.recv = __recv
PlayerStreamTrack.stop = lambda: None
PlayerStreamTrack.get_frame = __get_frame

