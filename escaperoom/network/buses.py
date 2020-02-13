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

    _group = Network.Group()

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
        return f'serialbus'

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
            except ConnectionRefusedError:
                self._set_connected(False)
                await asyncio.sleep(0)
            else:
                self._set_connected(True)

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
            result = await serial.send(dest, (msg).encode('ascii') + b'\0')
            if result is serial.proto.OutgoingResult.SUCCESS:
                self._log_debug(f'msg sent to 0x{dest:02x}: {msg}')
            else:
                self._log_error(f'failed to send: {msg}')

    async def broadcast(self, msg):
        return await self.send(0x0, msg)


class SocketBus(Bus):

    def __init__(self, host, port, *, bus_id, create_server=False):
        super().__init__()
        self.host, self.port = host, port
        self.bus_id = int(bus_id)
        if create_server:
            self.clients = set()
            cr = asyncio.start_server(self._handle_client, host, port)
            asyncio.run_until_complete(cr)
        self._reader, self._writer = None, None
        asyncio.create_task(self._connect(host, port))
        self.sending = self.Condition()

    def __str__(self):
        return f'socket [{self.host}:{self.port}](0x{self.bus_id:02x})'

    async def _handle_client(self, reader, writer):
        self.clients.add((reader, writer))
        while not reader.at_eof():
            line = await reader.readline()
            for client in self.clients:
                client[1].write(line)
        self.clients.discard((reader, writer))

    def _connect(self, host, port):
        while self.disconnected():
            try:
                self._reader, self._writer = yield from asyncio.open_connection(host, port)
            except ConnectionRefusedError:
                logger.warning(f'{self}: connection refused')
                #await asyncio.wait(5)
        asyncio.create_task(self._listener())

    async def _listener(self):
        while True:
            data = (await self._reader.readline()).decode()
            words = data.split(maxsplit=2)
            se, de, msg = int(words[0]), int(words[1]), str(words[2])[:-1]
            if (de == 0 or de == self.bus_id) and se != self.bus_id:
                async with self.packet_changed:
                    self.packet = se, msg
                    self.packet_changed.notify_all()
                logger.debug(f'{self} received [0x{se:02x}->0x{de:02x}] "{msg}"')

    async def send(self, dest, msg):
        data = f'{self.bus_id} {dest} {msg}\n'.encode()
        try:
            clients = self.clients
        except AttributeError:
            if self.disconnected():
                raise ConnectionError()
            clients = {(self._reader, self._writer)}
        async with self.sending:
            for client in clients:
                client[1].write(data)
        logger.debug(f'{self}: sent [0x{self.bus_id:02x}->0x{dest:02x}] "{msg}"')

    async def broadcast(self, msg):
        await self.send(0x0, msg)

    def disconnected(self):
        if self._reader is None or self._writer is None:
            return True
        return False

