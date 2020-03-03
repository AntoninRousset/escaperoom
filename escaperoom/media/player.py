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

from . import asyncio, logger
from ..subprocess import SubProcess
from ..utils import ensure_iter


def effect_worker(loop, track_in, track_out, effect, quit_event):

    while not quit_event.is_set():
        future = asyncio.run_coroutine_threadsafe(track_in._queue.get(), loop)
        frame = future.result()
        frame = effect(loop, frame)
        asyncio.run_coroutine_threadsafe(track_out._queue.put(frame), loop)


class MediaPlayer(aiom.MediaPlayer):

    def __init__(self, file, format=None, options={}, audio_effect=None,
                 video_effect=None):

        super().__init__(file, format, options)

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
                logger.error('container has not audio track')
                raise RuntimeError()
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
                logger.error('container has not video track')
                raise RuntimeError()
            self.__log_debug("Starting video effect worker thread")
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


class Audio():
    
    def __init__(self, files, *, loop=False, loop_last=False):
        import mpv
        self.player = mpv.MPV('pause', 'keep-open')
        self.ended = asyncio.Event()
        self.__loop = asyncio.get_event_loop()
        self.player.observe_property('pause', self._playing)
        if loop_last:
            self.player.observe_property('playlist-count', self._looping)
            self.player.observe_property('playlist-pos-1', self._looping)
        self._open(files)

    def __bool__(self):
        return not self.ended.is_set()

    def _playing(self, name, value):
        if value == True:
            self.__loop.call_soon_threadsafe(self.ended.set)
        elif value == False:
            self.__loop.call_soon_threadsafe(self.ended.clear)

    def _looping(self, n, v):
        if v is not None:
            if n == 'playlist-pos-1' and v == self.player.playlist_count:
                self.player.loop = True
            elif n == 'playlist-count' and v == self.player.playlist_count: 
                self.player.loop = True
        else:
            self.player.loop = False

    def _open(self, files):
        for file in ensure_iter(files):
            self.player.playlist_append(str(file))

    def play(self):
        if self.ended:
            self.player.playlist_pos = 0
            self.ended.clear()
        self.player.pause = False
        return asyncio.create_task(self.ended.wait())

    async def stop(self):
        self.player.pause = True
        self.ended.set()
