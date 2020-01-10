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

logger = logging.getLogger('escaperoom.misc')

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

class Display(ABC, Node):

    def __init__(self, name):
        super().__init__()
        self.name = name

    def __str__(self):
        return f'display "{self.name}"'

class LocalDisplay(Display):
    
    EXEC_NAME = 'escaperoom-display'

    def __init__(self, name, game=None):
        super().__init__(name)
        from subprocess import Popen
        from asyncio.subprocess import PIPE
        try:
            co = asyncio.create_subprocess_shell(self.EXEC_NAME, stdin=PIPE)
            self.ps = asyncio.run_until_complete(co)
        except FileNotFoundError:
            logger.error(f'{self}: could not find escaperoom-display')
            raise RuntimeError()
        if game is not None:
            self.game = game
            self.create_task(self._chronometer_listener())

    async def _chronometer_listener(self):
        while True:
            print('listening')
            async with self.game.desc_changed:
                data = {
                        'running' : ( self.game.start_time is not None and
                                      self.game.end_time is None ),
                        'seconds' : self.game.chronometer.total_seconds()
                        }
                self.create_task(self._send_chronometer(data))
                await self.game.desc_changed.wait()

    async def _send_chronometer(self, data):
        msg = f'chronometer {int(data["running"])} {data["seconds"]}\n'
        print('sending', data)
        try:
            self.ps.stdin.write(msg.encode())
            await self.ps.stdin.drain()
        except Exception as e:
            logger.error(f'{self} is dead: {e}')
            raise RuntimeError()

#TODO
class RemoteDisplay(Display):

    def __init__(self, name, address, game=None):
        super().__init__()
        self.address = address
        self.sending = asyncio.Lock()

    async def send(self, data):
        try:
            async with aiohttp.ClientSession() as s:
                async with s.post(self.address, data=json.dumps(data)) as r:
                    return 'done'
        except aiohttp.ClientConnectionError as e:
            logger.warning(f'cannot connect to display on {self.address}')
            raise e

