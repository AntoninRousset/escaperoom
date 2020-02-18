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

import re
from abc import abstractmethod
from aiortc import RTCPeerConnection, RTCSessionDescription

from . import asyncio, Misc
from ..media import MediaPlayer


class Camera(Misc):

    def __init__(self, name):
        super().__init__(name)
        self.connected = False 
        self._register(Camera)

    def __str__(self):
        return f'camera "{self.name}"'

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
        #prefered = 120 #vp8
        #prefered = 121 #vp9
        #prefered = '126 |109 ' #h264 and opus
        #prefered = '97 |109 ' #h264 and opus
        #sdp = re.sub(f'm=(video|audio) ([0-9]+) UDP\/TLS\/RTP\/SAVPF ([0-9 ]*)({prefered})([0-9 ]*)', r'm=\1 \2 UDP/TLS/RTP/SAVPF \4', sdp)
        #sdp = re.sub(f'a=rtpmap:(?!{prefered})\d* \w+\/.*\n?', '', sdp)
        #sdp = re.sub(f'a=fmtp:(?!{prefered}).*\n?', '', sdp)
        #sdp = re.sub(f'a=rtcp-fb:(?!{prefered}).*\n?', '', sdp)
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
            self._log_warning(f'error while connecting to camera on {self.address}')

