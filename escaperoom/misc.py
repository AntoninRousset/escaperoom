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

    async def _camera_listening(self, camera):
        while True: 
            async with camera.desc_changed:
                await camera.desc_changed.wait()
                logger.debug(f'Misc: Camera {camera} changed its desc')
                async with self.cameras_changed:
                    self.cameras_changed.notify_all()

    def add_camera(self, camera):
        uid = hex(id(camera))
        self.cameras[uid] = camera 
        self.create_task(self._camera_listening(camera))
        logger.debug('Misc: Camera added')
        return uid

    #TODO multiple displays
    def add_display(self, display):
        self.display = display

# Every msg on ws should be given to the camera so it can handle it
# Abstract class
class Camera(Node):
    def __init__(self, name):
        super().__init__()
        self.name = name
        self.connected = False 
        self.desc_changed = self.Condition()

class LocalCamera(Camera, MediaPlayer):
    def __init__(self, name, *args, **kwargs):
        Camera.__init__(self, name)
        MediaPlayer.__init__(self, *args, **kwargs)
        self.pcs = set()

    async def handle_offer(self, offer):
        pc = self.create_peer_connection()
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

    def create_peer_connection(self):
        pc = RTCPeerConnection()

        @pc.on('iceconnectionchanged')
        async def on_ice_connection_state_change():
            if pc.iceConnectionState == 'failed':
                await pc.close()
                pcs.discard(pc)

        return pc

class Display(Node):
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

