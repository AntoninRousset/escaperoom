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
    
    EXEC_ARGS = ['mpv', '--input-ipc-server={socket}', '--keep-open',
                 '--no-config', '--no-terminal', '--pause', 'idle=once']

    def __init__(self, files, *, loop=False, loop_last=False):
        self.loop = loop
        self.loop_last = loop_last
        self.socket = None
        self._requests = dict()
        self.end = asyncio.Event()
        self._need_check_last_file = asyncio.Event()
        self.last_file = None
        asyncio.create_task(self._last_file_checking())
        asyncio.run_until_complete(self._open())
        asyncio.run_until_complete(self.append_files(files))

    def __bool__(self):
        return not self.end.is_set()

    async def _open(self):
        socket = gettempdir() + '/mpv' + str(hex(id(self)))
        args = [arg.format(socket=socket) for arg in self.EXEC_ARGS]
        await SubProcess(socket, *args).running
        while True:
            try:
                accesses = await asyncio.open_unix_connection(socket)
                reader, self._socket = accesses
                asyncio.create_task(self._listener(reader))
                return
            except (FileNotFoundError, ConnectionRefusedError):
                await asyncio.sleep(0.1)

    async def _listener(self, reader):
        while True:
            try:
                line = await reader.readline()
                data = json.loads(line)
                for key, value in data.items():
                    if key == 'request_id':
                        request = self._requests.get(int(value))
                        if request is not None:
                            request[0].set()
                            request[1] = data
                    elif key == 'event':
                        if value == 'start-file':
                            self._need_check_last_file.set()
                        elif value == 'unpause':
                            self.end.clear()
                        elif value == 'pause':
                            self.end.set()
            except Exception as e:
                #print('error while reading audio player', e)
                pass

    async def __get_file_pos(self):
        p = await self._request({'command': ['get_property', 'playlist-pos-1']})
        n = await self._request({'command': ['get_property', 'playlist-count']})
        return p, n

    async def _last_file_checking(self):
        while True:
            await self._need_check_last_file.wait()
            try:
                p, n = await self.__get_file_pos()
            except RuntimeError as e:
                if str(e) != 'property unavailable':
                    raise
                await asyncio.sleep(0.1)
            else:
                await self._request({'command': ['set_property', 'loop-file',
                                                 (p == n) and self.loop_last]})
                self._need_check_last_file.clear()

    def __create_request(self):
        offset = 42
        for request_id in range(offset, offset+len(self._requests)+1):
            if request_id not in self._requests.keys():
                return request_id, [asyncio.Event(), None]

    async def _send(self, data: dict):
        line = json.dumps(data)+'\n'
        self._socket.write(line.encode())
        await self._socket.drain()

    async def _request(self, data: dict):
        request_id, request = self.__create_request()
        self._requests[request_id] = request

        data['request_id'] = request_id
        await self._send(data)

        await request[0].wait()
        self._requests.pop(request_id)
        response = request[1]
        if response['error'] != 'success':
            raise RuntimeError(response['error'])
        return response.get('data')

    async def _go_beginning(self):
        try:
            while True:
                await self._request({'command' : ['playlist-prev']}),
        except RuntimeError as e:
            if str(e) != 'error running command':
                raise

    async def append_files(self, files):
        for file in ensure_iter(files):
            await self._request({'command': ['loadfile', str(file), 'append']})
            self.last_file = file
        self._need_check_last_file.set()

    async def _play(self):
        await asyncio.gather(
            self._request({'command': ['set_property', 'loop', False]}),
            self._request({'command': ['set_property', 'loop-playlist',
                                       self.loop]})
            )
        if self.end.is_set():
            await self._go_beginning()
            self.end.clear()
        await self._request({'command': ['set_property', 'pause', False]})
        self._need_check_last_file.set()
        await self.end.wait()

    def play(self):
        return asyncio.create_task(self._play())

    async def stop(self):
        self.end.set()
        await self._request({'command': ['set_property', 'pause', True]})
