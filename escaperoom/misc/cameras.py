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

from abc import abstractmethod
import aiortc
import aiohttp
import atexit
import json
import logging

from . import asyncio, Misc
from ..media import MediaPlayer

logger = logging.getLogger('escaperoom.misc.cameras')


class Camera(Misc):

    def __init__(self, name):
        super().__init__(name)
        self.connected = False

    def __str__(self):
        return f'camera "{self.name}"'

    @abstractmethod
    async def handle_sdp(self, sdp, type):
        pass

    async def close(self):
        pass


class LocalCamera(Camera):

    @classmethod
    def get_codecs_capabilities(cls, type):
        codecs = aiortc.RTCRtpSender.getCapabilities(type).codecs
        return [codec for codec in codecs]

    def __init__(self, name, *, codec_prefs=None,
                 v_file, v_format=None, v_options={}, v_effect=None,
                 a_file=None, a_format='alsa', a_options={}, a_effect=None,
                 v4l2_ctl=None, always_running=False):
        super().__init__(name)
        self.pcs = set()
        self.codec_prefs = dict() if codec_prefs is None else codec_prefs

        if v4l2_ctl:
            self.set_v4l2_ctl(v_file, v4l2_ctl)

        self._player_options = {
            'v_file': v_file, 'v_format': v_format, 'v_options': v_options,
            'v_effect': v_effect, 'a_file': a_file, 'a_format': a_format,
            'a_options': a_options, 'a_effect': a_effect,
            'always_running': always_running,
        }

        self.v_player = None
        self.a_player = None
        self._open_players(**self._player_options)

    def _open_players(self, v_file, v_format, v_options, v_effect, a_file,
                      a_format, a_options, a_effect, always_running):

        try:
            self.v_player = MediaPlayer(v_file, v_format, v_options,
                                        a_effect=a_effect, v_effect=v_effect,
                                        always_running=always_running)

            if a_file is None:
                self.a_player = self.v_player
            else:
                self.a_player = MediaPlayer(a_file, a_format, a_options)

        except Exception:
            logger.exception(f'Cannot open players')

    @staticmethod
    def set_v4l2_ctl(devfile, ctl):
        from subprocess import run, PIPE, CalledProcessError
        for k, v in ctl.items():
            try:
                run(['v4l2-ctl', '-d', str(devfile), '-c', f'{k}={v}'],
                    stdout=PIPE, stderr=PIPE, check=True)
            except CalledProcessError as e:
                logger.exception(f'Failed to set v4l2-ctl {k}={v}:\n'
                                 f'{e.stderr.decode()}')
            except BaseException:
                logger.exception(f'Failed to set v4l2-ctl {k}={v}')

    def _create_peer_connection(self):
        pc = aiortc.RTCPeerConnection()

        @pc.on('iceconnectionstatechange')
        async def on_iceconnectionstatechange():
            logger.info(f'ice state: {pc.iceConnectionState}')
            if pc.iceConnectionState == 'failed':
                await self._close_pc(pc)

        return pc

    def _set_codec_preferences(self, transceiver):
        def lt(a, b):
            x, y = a.name, b.name
            if x not in self.codec_prefs:
                if y not in self.codec_prefs:
                    return False
                return False
            elif y not in self.codec_prefs:
                return True
            return self.codec_prefs[y] - self.codec_prefs[x] < 0
        aiortc.RTCRtpCodecCapability.__lt__ = lt
        prefs = sorted(self.get_codecs_capabilities('video'))
        transceiver.setCodecPreferences(prefs)

    async def handle_sdp(self, sdp, type):

        while True:
            try:
                offer = aiortc.RTCSessionDescription(sdp, type)
                pc = self._create_peer_connection()
                self.pcs.add(pc)
                await pc.setRemoteDescription(offer)

                if self.v_player is None and self.a_player is None:
                    self._open_players(**self._player_options)

                for t in pc.getTransceivers():
                    if t.kind == 'audio' and self.audio:
                        pc.addTrack(self.audio)
                    elif t.kind == 'video' and self.v_player:
                        pc.addTrack(self.video)

                answer = await pc.createAnswer()
                await pc.setLocalDescription(answer)
                return {'sdp': pc.localDescription.sdp,
                        'type': pc.localDescription.type}

            except BaseException:
                logger.exception('Failed to handle sdp. Resetting players.')
                self.v_player = None
                self.a_player = None
                await asyncio.sleep(1)

    async def _close_pc(self, pc):
        try:
            await pc.close()
        except BaseException:
            logger.exception(f'Failed to close pc')
        self.pcs.discard(pc)

    async def close(self):
        await asyncio.wait({self._close_pc(pc) for pc in self.pcs})

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
                data = {'sdp': sdp, 'type': type}
                async with s.post(address, data=json.dumps(data)) as r:
                    response = await r.json()
                    return response['data']
        except aiohttp.ClientError:
            self._log_warning('error while connecting to camera on '+
                              self.address)
