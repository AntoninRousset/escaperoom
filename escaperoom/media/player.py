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

import aiortc.contrib.media as aiom
import threading, json
#import alsaaudio as alsa
from tempfile import gettempdir

from . import asyncio, logger, Media
from ..subprocess import SubProcess
from ..utils import ensure_iter


aiom.MediaStreamTrack.stop = lambda: None #TMP, TODO

def effect_worker(loop, track_in, track_out, effect, quit_event):

    print_warning = True

    while not quit_event.is_set():
        future = asyncio.run_coroutine_threadsafe(track_in._queue.get(), loop)
        frame = future.result()

        try:
            frame = effect(loop, frame)
            print_warning = True
        except BaseException:
            if print_warning:
                logger.exception('Failed to apply video effect')
                print_warning = False

        asyncio.run_coroutine_threadsafe(track_out._queue.put(frame), loop)


class MediaPlayer(aiom.MediaPlayer):

    def __init__(self, file, format=None, options={}, audio_effect=None,
                 video_effect=None):

        super().__init__(str(file), format, options)

        self.__audio_effect = audio_effect
        self.__video_effect = video_effect
        self.__audio_with_effect = aiom.PlayerStreamTrack(self, kind='audio')
        self.__video_with_effect = aiom.PlayerStreamTrack(self, kind='video')
        self.__effect_audio_thread = None
        self.__effect_audio_thread_quit = None
        self.__effect_video_thread = None
        self.__effect_video_thread_quit = None

    def _start(self, track):

        super()._start(track)

        if self.__effect_audio_thread is None and self.__audio_effect is not None:
            if self.__audio is None:
                raise RuntimeError('container has not audio track')
            self.__log_debug('Starting audio effect worker thread')
            self.__effect_audio_thread_quit = threading.Event()
            args = (asyncio.get_event_loop(), self.__audio,
                    self.__audio_with_effect,
                    self.__audio_effect,
                    self.__effect_audio_thread_quit)
            self.__effect_audio_thread = threading.Thread(name='audio_effect',
                                                          target=effect_worker,
                                                          args=args)
            self.__effect_audio_thread.start()

        if self.__effect_video_thread is None and self.__video_effect is not None:
            if self.__video is None:
                raise RuntimeError('container has not video track')
            self.__log_debug('Starting video effect worker thread')
            self.__effect_video_thread_quit = threading.Event()
            args = (asyncio.get_event_loop(), self.__video,
                    self.__video_with_effect,
                    self.__video_effect,
                    self.__effect_video_thread_quit)
            self.__effect_video_thread = threading.Thread(name='video_effect',
                                                          target=effect_worker,
                                                          args=args)
            self.__effect_video_thread.start()

    @property
    def audio(self):
        if self.__audio_effect is None:
            return self.__audio
        return self.__audio_with_effect

    @property
    def video(self):
        if self.__video_effect is None:
            return self.__video
        return self.__video_with_effect

    def _stop(self, track):

        if not self.__started and self.__effect_audio_thread:
            self.__log_debug("Stopping audio effect worker thread")
            self.__effect_audio_thread_quit.set()
            self.__effect_audio_thread.join()
            self.__effect_audio_thread = None

        if not self.__started and self.__effect_video_thread:
            self.__log_debug("Stopping video effect worker thread")
            self.__effect_video_thread_quit.set()
            self.__effect_video_thread.join()
            self.__effect_video_thread = None

        super()._stop(track)


from sdl2 import *
from sdl2.ext.compat import byteify
from sdl2.sdlmixer import *

import ctypes
import threading 

class Audio(Media):

    _channels_groups_lock = threading.Lock()
    _channels_groups = list()

    if SDL_Init(SDL_INIT_AUDIO) != 0:
        raise RuntimeError('Cannot initialize audio: '+SDL_GetError())
    if Mix_OpenAudio(44100, MIX_DEFAULT_FORMAT, 2, 1024):
        raise RuntimeError('Cannot open mixed audio: '+Mix_GetError())

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
