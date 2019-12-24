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

from . import config 
from .media import MediaPlayer
from .node import Node 

def misc_debug(msg):
    if config['DEFAULT'].getboolean('misc_debug', False):
        print(msg)

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
                misc_debug(f'Misc: Camera {camera} changed its desc')
                async with self.cameras_changed:
                    self.cameras_changed.notify_all()

    def add_camera(self, camera):
        uid = hex(id(camera))
        self.cameras[uid] = camera 
        self.create_task(self._camera_listening(camera))
        misc_debug('Misc: Camera added')
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
    def __init__(self, address):
        super().__init__()
        self.address = address

    async def handle(self, data):
        async with aiohttp.ClientSession() as session:
            async with session.post(self.address, data=json.dumps(data)) as resp:
                return 'done'
