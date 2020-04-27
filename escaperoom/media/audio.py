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

from . import asyncio, Media
from ..utils import ensure_iter

from sdl2 import SDL_Init, SDL_INIT_AUDIO, SDL_GetError
from sdl2.ext.compat import byteify
from sdl2.sdlmixer import (Mix_OpenAudio, MIX_DEFAULT_FORMAT, Mix_GetError,
                           Mix_GroupChannel, Mix_LoadWAV, Mix_PlayChannel,
                           Mix_HaltGroup, Mix_ChannelFinished)

import ctypes
import threading


class Audio(Media):

    _channels_groups_lock = threading.Lock()
    _channels_groups = list()

    if SDL_Init(SDL_INIT_AUDIO) != 0:
        raise RuntimeError('Cannot initialize audio: ' + SDL_GetError())
    if Mix_OpenAudio(44100, MIX_DEFAULT_FORMAT, 2, 1024):
        raise RuntimeError('Cannot open mixed audio: ' + Mix_GetError())

    @classmethod
    def _channel_finished(cls, channel):
        def find_player(channel):
            with cls._channels_groups_lock:
                for group in cls._channels_groups:
                    if channel in group:
                        return group[channel]
                raise KeyError(channel)
        try:
            player, sample = find_player(channel)
            player._sample_ended(sample, channel)
        except KeyError:
            pass

    @classmethod
    def _create_channels_group(cls):
        with cls._channels_groups_lock:
            cls._channels_groups.append(dict())
            return len(cls._channels_groups) - 1

    def __init__(self, files, *, loop=False, loop_last=False):
        files = ensure_iter(files)
        super().__init__(', '.join(map(str, files)))
        self.loop = loop
        self.loop_last = loop_last
        self.__loop = asyncio.get_event_loop()
        self._samples = list()
        self.__group_id = self._create_channels_group()
        self._stoping = False
        self._ended = asyncio.Event()
        self._ended.set()
        self._open(files)

    def __bool__(self):
        return bool(self.__channels_group)

    def __str__(self):
        return f'sound "{self.name}"'

    async def wait(self):
        await self._ended.wait()

    @property
    def __channels_group(self):
        return self._channels_groups[self.__group_id]

    def _sample_ended(self, sample, channel):
        try:
            if self._stoping:
                raise StopIteration()
            samples = iter(self._samples)
            while True:
                if next(samples) is sample:
                    next_sample = next(samples)
                    loop = self.loop_last and next_sample is self._samples[-1]
                    return self._play(next_sample, channel, loop=loop)
        except StopIteration:
            if not Mix_GroupChannel(channel, -1):
                print('ERROR, cannot remove channel from group')
            with self._channels_groups_lock:
                self.__channels_group.pop(channel)
            if not self:
                self.__loop.call_soon_threadsafe(self._ended.set)

    def _open(self, files):
        for file in files:
            sample = Mix_LoadWAV(byteify(str(file), 'utf-8'))
            if sample is None:
                raise RuntimeError('Cannot open audio file: '+Mix_GetError())
            self._samples.append(sample)

    def _play(self, sample, channel=-1, *, loop=False):
        self._ended.clear()
        channel = Mix_PlayChannel(channel, sample, -1 if loop else 0)
        if not Mix_GroupChannel(channel, self.__group_id):
            print('ERROR, cannot remove channel from group')
        with self._channels_groups_lock:
            self.__channels_group[channel] = (self, sample)

    def play(self):
        self._play(self._samples[0], loop=self.loop)
        return asyncio.create_task(self._ended.wait())

    async def _reset(self):
        self._stoping = True
        Mix_HaltGroup(self.__group_id)
        await self._ended.wait()
        self._stoping = False

    def stop(self):
        return asyncio.create_task(self._reset())


c_wrapper = ctypes.CFUNCTYPE(None, ctypes.c_int)
c_func = c_wrapper(Audio._channel_finished)
Mix_ChannelFinished(c_func)
