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
from . import asyncio
import logging, threading

logger = logging.getLogger('misc')

def effect_worker(loop, track_in, track_out, effect, quit_event):

    while not quit_event.is_set():
        future = asyncio.run_coroutine_threadsafe(track_in._queue.get(), loop)
        frame = future.result()
        frame = effect(frame)
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
        print('audio with effect!')
        return self.__audio_with_effect

    @property
    def video(self):
        if self.__video_effect is None:
            return self.__video
        print('video with effect!')
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


'''
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
'''
