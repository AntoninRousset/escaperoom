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

from abc import ABC, abstractmethod

from . import logger, Node
from .media import MediaPlayer

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
        prefered = 120 #vp8
        #sdp = re.sub(f'm=video ([0-9]+) UDP\/TLS\/RTP\/SAVPF ([0-9 ]*)({prefered})[ ]*([0-9 ]*)', r'm=video \1 UDP/TLS/RTP/SAVPF \3 \2\4', sdp)
        sdp = re.sub(f'm=video ([0-9]+) UDP\/TLS\/RTP\/SAVPF ([0-9 ]*)({prefered})[ ]*([0-9 ]*)', r'm=video \1 UDP/TLS/RTP/SAVPF \3', sdp)
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
        return self.a_player.audio

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

