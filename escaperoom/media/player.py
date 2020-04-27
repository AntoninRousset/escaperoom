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
import threading

from . import asyncio, logger
import av
import aiortc
import aiortc.contrib.media as aiom
from aiortc.mediastreams import AUDIO_PTIME, MediaStreamError, MediaStreamTrack
from threading import Lock
from weakref import ref

# TMP, TODO
aiom.MediaStreamTrack.stop = lambda: None


def worker(loop, container, streams, tracks, lock_tracks, quit_event):

    import fractions

    audio_fifo = av.AudioFifo()
    audio_format_name = "s16"
    audio_layout_name = "stereo"
    audio_sample_rate = 48000
    audio_samples = 0
    audio_samples_per_frame = int(audio_sample_rate * AUDIO_PTIME)
    audio_resampler = av.AudioResampler(format=audio_format_name,
                                        layout=audio_layout_name,
                                        rate=audio_sample_rate)

    video_first_pts = None
    print('work')

    def iter_tracks(kind=None):
        with lock_tracks:

            # clean invalid ref
            tt = {t for t in tracks if t() is not None}

            for track in tt:
                track = track()
                if track is not None:
                    if kind is None or kind == track.kind:
                        yield track

    while not quit_event.is_set():


        # decode frame
        try:
            frame = next(container.decode(*streams))
        except (av.AVError, StopIteration):
            for track in iter_tracks():
                asyncio.run_coroutine_threadsafe(track._queue.put(None), loop)
            break

        # audio
        if isinstance(frame, av.AudioFrame) and set(iter_tracks('audio')):

            if (
                frame.format.name != audio_format_name
                or frame.layout.name != audio_layout_name
                or frame.sample_rate != audio_sample_rate
            ):
                frame.pts = None
                frame = audio_resampler.resample(frame)

            # fix timestamps
            frame.pts = audio_samples
            frame.time_base = fractions.Fraction(1, audio_sample_rate)
            audio_samples += frame.samples

            audio_fifo.write(frame)
            while True:
                frame = audio_fifo.read(audio_samples_per_frame)
                if frame:
                    for track in iter_tracks('audio'):
                        asyncio.run_coroutine_threadsafe(
                            track._queue.put(frame), loop)
                else:
                    break

        # video
        if isinstance(frame, av.VideoFrame) and set(iter_tracks('video')):

            if frame.pts is None:  # pragma: no cover
                logger.warning("Skipping video frame with no pts")
                continue

            # video from a webcam doesn't start at pts 0, cancel out offset
            if video_first_pts is None:
                video_first_pts = frame.pts
            frame.pts -= video_first_pts

            for track in iter_tracks('video'):
                asyncio.run_coroutine_threadsafe(track._queue.put(frame), loop)


class PlayerStreamTrack(MediaStreamTrack):

    def __init__(self, kind):
        super().__init__()
        self.kind = kind
        self._queue = asyncio.Queue()
        logger.debug('WebcamStreamTrack created')

    async def recv(self):

        print(self.readyState)

        if self.readyState != "live":
            raise MediaStreamError

        frame = await self._queue.get()

        # TODO why stop if no frame?
        if frame is None:
            self.stop()
            raise MediaStreamError

        print(frame)

        return frame


class MediaPlayer(aiom.MediaPlayer):
    """
    Multiqeue media player with optional effects.
    """

    def __init__(self, file, format=None, options={}):

        super().__init__(file, format, options)

        self.__lock_started = Lock()

        # TODO if self.__started is empty, do not run worker
        self.__thread_quit = threading.Event()
        self.__thread = threading.Thread(
            name="media-player",
            target=worker,
            args=(
                asyncio.get_event_loop(),
                self.__container,
                self.__streams,
                self.__started,
                self.__lock_started,
                self.__thread_quit,
            ),
        )
        self.__thread.start()
        logger.debug(f'WebcamSource created file: {file},'
                     f'format: {format}, options: {options}')

    @property
    def audio(self):
        track = PlayerStreamTrack(kind='audio')
        self._start(track)
        return track

    @property
    def video(self):
        track = PlayerStreamTrack(kind='video')
        self._start(track)
        return track

    def _start(self, track):
        with self.__lock_started:
            track = ref(track) if not isinstance(track, ref) else track
            self.__started.add(track)

    def _stop(self, track):
        with self.__lock_started:
            track = ref(track) if not isinstance(track, ref) else track
            self.__started.discard(track)


'''
class MediaPlayer(aiom.MediaPlayer):

    def __init__(self, file, format=None, options={}, audio_effect=None,
                 video_effect=None):

        super().__init__(str(file), format, options)

        self.__audio_effect = audio_effect
        self.__video_effect = video_effect

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
'''

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



