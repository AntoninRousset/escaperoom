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

import aiohttp, json, re
from aiortc import RTCPeerConnection, RTCSessionDescription
from abc import ABC, abstractmethod

from . import asyncio, logging 
from .media import MediaPlayer
from .node import Node 

logger = logging.getLogger('escaperoom.misc')

class Camera(ABC, Node):

    cameras = dict()

    def __init__(self, name):
        super().__init__()
        self.name = name
        self.connected = False 
        self.desc_changed = self.Condition()
        self.cameras_changed = self.Condition()
        self.add_camera(self)

    def __str__(self):
        return f'camera "{self.name}"'

    async def _camera_listening(self, camera):
        while True: 
            async with camera.desc_changed:
                await camera.desc_changed.wait()
                logger.debug(f'{self}: {camera} changed its desc')
                async with self.cameras_changed:
                    self.cameras_changed.notify_all()

    @classmethod
    def find_camera(cls, *, id=None, name=None):
        if id is not None:
            return id, cls.cameras[id]
        for id, camera in cls.cameras.items():
            if re.match(name, camera.name):
                return id, camera

    def add_camera(self, camera):
        _id = hex(id(camera))
        self.cameras[_id] = camera 
        self.create_task(self._camera_listening(camera))

    @abstractmethod
    async def handle_sdp(self, sdp, type):
        pass

class LocalCamera(Camera):
    def __init__(self, name, *, v_file, v_format=None, v_options={}, a_file=None,
                 a_format='alsa', a_options={}, a_effect=None, v_effect=None):
        super().__init__(name)
        self.v_player = MediaPlayer(v_file, v_format, v_options)
        if a_file is None:
            self.a_player = self.v_player
        else:
            self.a_player = MediaPlayer(a_file, a_format, a_options)
        self.pcs = set()

    def _create_peer_connection(self):
        pc = RTCPeerConnection()

        @pc.on('iceconnectionchanged')
        async def on_ice_connection_state_change():
            if pc.iceConnectionState == 'failed':
                await pc.close()
                pcs.discard(pc)
        return pc

    async def handle_sdp(self, sdp, type):
        offer = RTCSessionDescription(sdp, type)
        pc = self._create_peer_connection()
        self.pcs.add(pc)
        await pc.setRemoteDescription(offer)
        for t in pc.getTransceivers():
            if t.kind == 'audio' and self.audio:
                pc.addTrack(self.audio)
            elif t.kind == 'video' and self.video:
                pc.addTrack(self.video)
        answer = await pc.createAnswer()
        await pc.setLocalDescription(answer)
        return {'sdp' : pc.localDescription.sdp, 'type' : pc.localDescription.type}

    @property
    def audio(self):
        return self.v_player.audio
        #return self.a_player.audio

    @property
    def video(self):
        return self.v_player.video

class RemoteCamera(Camera):

    def __init__(self, name, address, *, rename=None):
        if rename is None:
            rename = name
        super().__init__(rename)
        self.address = address
        self.remote_name = name
        
    async def handle_sdp(self, sdp, type):
        try:
            async with aiohttp.ClientSession() as s:
                address = self.address + f'/camera?name={self.remote_name}'
                data = {'sdp' : sdp, 'type' : type}
                async with s.post(address, data=json.dumps(data)) as r:
                    return await r.json()
        except aiohttp.ClientError as e:
            logger.warning(f'error while connecting to camera on {self.address}')

class Display(ABC, Node):

    displays = dict()

    def __init__(self, name, game=None):
        super().__init__()
        self.name = name
        if game is not None:
            self.game = game
            self.create_task(self._chronometer_listener())
        self.add_display(self)

    def __str__(self):
        return f'display "{self.name}"'

    async def _chronometer_listener(self):
        while True:
            async with self.game.desc_changed:
                runn = self.game.start_time is not None and self.game.end_time is None
                seconds = self.game.chronometer.total_seconds()
                self.create_task(self.set_chronometer(runn, seconds))
                await self.game.desc_changed.wait()

    def add_display(self, display):
        _id = hex(id(display))
        self.displays[_id] = display

    @classmethod
    def find_display(cls, *, id=None, name=None):
        for id, display in cls.displays.items():
            if id is not None:
                return id, cls.displays[id]
            for id, display in cls.displays.items():
                if re.match(name, display.name):
                    return id, display

    @abstractmethod
    async def set_chronometer(self, running, seconds):
        pass

    @abstractmethod
    async def set_msg(self, msg):
        pass


class LocalDisplay(Display):
    
    EXEC_NAME = 'escaperoom-display'

    def __init__(self, name, game=None):
        super().__init__(name, game)
        from subprocess import Popen
        from asyncio.subprocess import PIPE
        try:
            co = asyncio.create_subprocess_shell(self.EXEC_NAME, stdin=PIPE)
            self.ps = asyncio.run_until_complete(co)
        except FileNotFoundError:
            logger.error(f'{self}: could not find escaperoom-display')
            raise RuntimeError()

    async def _write_to_process(self, data):
        #TODO should not be called before display is ready
        try:
            self.ps.stdin.write(data)
            await self.ps.stdin.drain()
        except Exception as e:
            logger.error(f'{self} is dead: {e}')
            raise RuntimeError()

    async def set_chronometer(self, running, seconds):
        msg = f'chronometer {int(running)} {seconds}\n'
        await self._write_to_process(msg.encode())

    async def set_msg(self, msg):
        msg = f'msg {msg}\n'
        await self._write_to_process(msg.encode())

#TODO? create a "Remote" class which defines the _send(data) method
class RemoteDisplay(Display):

    def __init__(self, name, address, game=None, *, rename=None):
        if rename is None:
            rename = name
        super().__init__(rename, game)
        self.address = address
        self.remote_name = name

    async def set_chronometer(self, running, seconds):
        data = {'type' : 'chronometer', 'running' : running, 'seconds' : seconds}
        await self._send(data)

    async def set_msg(self, msg):
        await self._send({'type' : 'msg', 'msg' : msg})

    async def _send(self, data):
        try:
            async with aiohttp.ClientSession() as s:
                address = self.address + f'/display?name={self.remote_name}'
                async with s.post(address, data=json.dumps(data)) as r:
                    return await r.json()
        except aiohttp.ClientError as e:
            logger.warning(f'error while connecting to camera on {self.address}')
            #TODO? retry with "sending" lock?

