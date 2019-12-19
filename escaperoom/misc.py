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
from aiortc.contrib.media import MediaStreamTrack, MediaPlayer

MediaStreamTrack.stop = lambda: None

from . import config 
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

class LocalCamera(Camera):
    def __init__(self, name, path, format='v4l2'):
        super().__init__(name)
        self.path = path #do udev device instead
        self.format = format
        self.pcs = set()
        self.player = None
        self.player_changed = self.Condition()

    async def get_player(self):
        async with self.player_changed:
            if not self.player: 
                self.player = MediaPlayer(self.path, format=self.format)
                self.player_changed.notify_all()

    async def handle_offer(self, offer):
        await self.get_player()
        pc = self.create_peer_connection()
        self.pcs.add(pc)
        await pc.setRemoteDescription(offer)
        for t in pc.getTransceivers():
            if t.kind == 'audio' and self.player.audio:
                pc.addTrack(self.player.audio)
            elif t.kind == 'video' and self.player.video:
                pc.addTrack(self.player.video)
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

try:
    from picamera import PiCamera
except ImportError:
    pass
else:
    from io import BytesIO

    class LocalPiCamera(PiCamera, LocalCamera):
        def __init__(self, name):
            stream = BytesIO()
            PiCamera.__init__()
            camera.start_recording(stream, format='h264', quality=23)
            LocalCamera(name, stream, format='h264')

class Display(Node):
    def __init__(self, address):
        super().__init__()
        self.address = address

    async def handle(self, data):
        async with aiohttp.ClientSession() as session:
            async with session.post(self.address, data=json.dumps(data)) as resp:
                return 'done'
