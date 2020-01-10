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

import aiohttp, json
from aiortc import RTCPeerConnection, RTCSessionDescription
from abc import ABC, abstractmethod

from . import asyncio, logging 
from .media import MediaPlayer
from .node import Node 

logger = logging.getLogger('misc')

class Misc(Node):
    def __init__(self):
        super().__init__()
        self.cameras = dict()
        self.cameras_changed = self.Condition()
        self.display = None

    def __str__(self):
        return 'misc'

    async def _camera_listening(self, camera):
        while True: 
            async with camera.desc_changed:
                await camera.desc_changed.wait()
                logger.debug(f'{self}: {camera} changed its desc')
                async with self.cameras_changed:
                    self.cameras_changed.notify_all()

    def find_camera(self, *, id=None, name=None):
        if id is not None:
            return id, self.cameras[id]
        for id, camera in self.cameras.items():
            if camera.name == name:
                return id, camera

    def add_camera(self, camera):
        _id = hex(id(camera))
        self.cameras[_id] = camera 
        self.create_task(self._camera_listening(camera))
        logger.debug(f'{self}: {camera} added')
        return _id

    #TODO multiple displays
    def add_display(self, display):
        self.display = display

class Camera(ABC, Node):
    def __init__(self, name):
        super().__init__()
        self.name = name
        self.connected = False 
        self.desc_changed = self.Condition()

    def __str__(self):
        return f'camera "{self.name}"'

    @abstractmethod
    async def handle_sdp(self, sdp, type):
        pass

class LocalCamera(Camera, MediaPlayer):
    def __init__(self, name, *args, **kwargs):
        Camera.__init__(self, name)
        MediaPlayer.__init__(self, *args, **kwargs)
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
        except aiohttp.ClientConnectionError as e:
            logger.warning(f'cannot connect to camera on {self.address}')
            raise e

class RemoteDisplay(Node):
    def __init__(self, address, game=None):
        super().__init__()
        self.address = address
        if game is not None:
            self.create_task(self._chronometer_listener(game))
        self.sending = asyncio.Lock()

    async def _chronometer_listener(self, game):
        while True:
            async with game.desc_changed:
                self.create_task(self._send_chronometer(game))
                await game.desc_changed.wait()

    async def _send_chronometer(self, game):
        async with self.sending:
            while True:
                try:
                    running = game.start_time is not None and game.end_time is None
                    data = {'type' : 'chronometer', 'running' : running,
                            'seconds' : game.chronometer.total_seconds()}
                    return await self.send(data)
                except aiohttp.ClientConnectionError:
                    await asyncio.sleep(2)

    async def send(self, data):
        try:
            async with aiohttp.ClientSession() as s:
                async with s.post(self.address, data=json.dumps(data)) as r:
                    return 'done'
        except aiohttp.ClientConnectionError as e:
            logger.warning(f'cannot connect to display on {self.address}')
            raise e

