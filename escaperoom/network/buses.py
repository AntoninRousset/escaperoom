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

from . import config
if config['DEFAULT'].getboolean('test'):
    from . import serial_test as serial
else:
    import PJON_daemon_client as serial

from . import asyncio, Network

class Bus(Network):

    def __init__(self, name=None):
        super().__init__(name)
        self.packet = None
        self.packet_changed = asyncio.Condition()


class SerialBus(Bus):

    def __init__(self, path):
        super().__init__()
        self.path = path
        asyncio.create_task(self._listener())
        self.sending = asyncio.Condition()
        self._connected = asyncio.Event()

    def __str__(self):
        return f'[serialbus on {self.path}]'

    async def _listener(self):
        while True:
            try:
                async for packet in serial.listen():
                    if isinstance(packet, serial.proto.PacketIngoingMessage):
                        packet = packet.src, str(packet.data.decode('ascii'))[:-1]
                        async with self.packet_changed:
                            self.packet = packet
                            self.packet_changed.notify_all()
                        self._log_debug(f'received packet for {packet[0]}')
                    self._set_connected(True)
            except ConnectionRefusedError:
                self._set_connected(False)
                await asyncio.sleep(1)

    def _set_connected(self, state: bool):
        if state:
            if not self._connected.is_set():
                self._log_info('connected')
            self._connected.set()
        else:
            if self._connected.is_set():
                self._log_warning('disconnected')
            self._connected.clear()

    async def send(self, dest, msg):
        async with self.sending:
            #await asyncio.sleep(0.5)
            #TODO avoid bus saturation
            result = await serial.send(dest, (msg).encode('ascii') + b'\0')
            if result is serial.proto.OutgoingResult.SUCCESS:
                self._log_debug(f'msg sent to 0x{dest:02x}: {msg}')
            else:
                self._log_error(f'failed to send: {msg}')

    async def broadcast(self, msg):
        return await self.send(0x0, msg)

