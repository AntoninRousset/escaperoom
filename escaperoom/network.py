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

import logging, re
import PJON_daemon_client as pac

from . import asyncio
from .node import Node

logger = logging.getLogger('network')

class Bus(Node):

    def __init__(self):
        super().__init__()
        self.desc_changed = self.Condition()
        self.packet = None
        self.packet_changed = self.Condition()

class SerialBus(Bus):

    def __init__(self, path):
        super().__init__()
        self.path = path
        self.create_task(self._listener())
        self.sending = self.Condition()

    def __str__(self):
        return f'serial [{self.path}]'

    async def _listener(self):
        while True:
            try:
                async for packet in pac.listen():
                    if isinstance(packet, pac.proto.PacketIngoingMessage):
                        device_id = packet.src
                        msg = packet.data.decode('ascii')
                        packet = (device_id, str(msg)[:-1])
                        async with self.packet_changed:
                            self.packet = packet
                            self.packet_changed.notify_all()
                        logger.debug(f'{self} received packet for {device_id}')
            except ConnectionRefusedError:
                logger.warning(f'{self}: disconnected')
                await asyncio.sleep(5)

    async def send(self, dest, msg):
        async with self.sending:
            result = await pac.send(dest, (msg).encode('ascii') + b'\0')
            if result is pac.proto.OutgoingResult.SUCCESS:
                logger.debug(f'{self}: msg sent to 0x{dest:02x}: {msg}')
            else:
                logger.error(f'{self}: failed to send: {msg}')

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

class Network(Node):

    def __init__(self):
        super().__init__()
        self.packet = None
        self.packet_changed = self.Condition()
        self.buses = dict()
        self.buses_changed = self.Condition()
        self.devices = dict()
        self.devices_changed = self.Condition()

    def __str__(self):
        return 'network'

    async def _device_radar(self, bus):
        while bus in self.buses.values():
            try:
                await bus.broadcast('get desc')
            except Exception as e: 
                logger.warning(f'{self}: {e}')
            await asyncio.sleep(5)

    async def _bus_listening(self, bus):
        while bus in self.buses.values(): 
            async with bus.packet_changed:
                if bus.packet is not None:
                    device_id, msg = bus.packet
                    addr = (bus, device_id) 
                    async with self.packet_changed:
                        self.packet = (addr, msg) 
                        self.packet_changed.notify_all()
                        await self.read_msg(addr, msg)
                await bus.packet_changed.wait()

    def _find_device(self, addr=None, name=None):
        for device in self.devices.values():
            if not device.disconnected() and device.addr == addr:
                return device
            elif not device.disconnected() and device.addr[0] == addr[0] and addr[1] == 0:
                return device
            elif device.name == name:
                return device

    async def read_msg(self, sender, msg): 
        logger.debug(f'{self}: reading msg "{msg}"') 
        if re.match('\s*desc\s+\w+\s+\w+\s*', msg):
            name = msg.split()[1]
            device = self._find_device(sender, name)
            if device is None:
                logger.debug(f'{self}: no device with id 0x{sender[1]:02x}')
                device = Device(addr=sender, name=name)
                async with self.devices_changed:
                    self.add_device(device)
                    self.devices_changed.notify_all()
            else:
                logger.debug(f'{self}: found device with id 0x{sender[1]:02x}')
                async with device.desc_changed:
                    if device.addr != sender or device.name != name:
                        device.desc_changed.notify_all()
                    device.addr, device.name = sender, name
        device = self._find_device(sender)
        if device is None:
            logger.warning(f'Cannot find device with id 0x{sender[1]:02x}')
        else:
            await device.read_msg(msg)

    async def _device_listening(self, device):
        while device in self.devices.values(): 
            async with device.desc_changed:
                await device.desc_changed.wait()
                logger.debug(f'Network: Device {device} changed its desc')
                async with self.devices_changed:
                    self.devices_changed.notify_all()

    def add_bus(self, bus):
        uid = hex(id(bus))
        self.buses[uid] = bus
        self.create_task(self._device_radar(bus))
        self.create_task(self._bus_listening(bus))
        logger.debug(f'{self}: {bus} added')
        return uid

    def add_device(self, device):
        uid = hex(id(device))
        self.devices[uid] = device
        self.create_task(self._device_listening(device))
        logger.debug(f'{self}: {device} added')
        return uid

class Device(Node):

    def __init__(self, *, addr=None, name=None, type='unknown'): 
        super().__init__()
        self.addr = addr
        self.name = name
        self.type = type
        self.desc_changed = self.Condition()
        self.msg = None
        self.msg_changed = self.Condition()
        self.attrs = dict()
        self.attrs_changed = self.Condition()

    def __str__(self):
        if self.name is not None:
            return f'device "{self.name}"'
        elif not self.disconnected():
            return f'device {self.addr[1]}@{self.addr[0]}'
        else:
            return 'device'

    async def _attr_listening(self, attr):
        while attr in self.attrs.values(): 
            async with attr.desc_changed: 
                await attr.desc_changed.wait()
                async with self.attrs_changed:
                    self.attrs_changed.notify_all()

    def add_attr(self, attr):
        if attr.attr_id is None:
            attr.attr_id = len(self.attrs)
        uid = hex(id(attr)) 
        self.attrs[uid] = attr
        self.create_task(self._attr_listening(attr))
        logger.debug(f'{self}: {attr} added')

    async def read_msg(self, msg):
        pass

    async def remove_attr(self, attr_id, name):
        async with self.attrs_changed:
            for uid, attr in self.attrs.items():
                if attr.name == name:
                    return self.attrs.remove(uid)
                elif attr.attr_id == attr_id:
                    return self.attrs.remove(uid)

    def _find_attr(self, attr_id=None, name=None):
        for attr in self.attrs.values():
            if name is not None and attr.name == name:
                return attr
            elif attr.attr_id == attr_id:
                return attr

    @property
    def attrs_ids(self):
        return {a.attr_id for a in self.attrs.values() if a.attr_id is not None}

    def disconnected(self):
        return False

class LocalDevice(Device):

    def __init__(self, *, addr, name, type='unknown'):
        super().__init__(addr=addr, name=name, type=type)
        self.create_task(self._bus_listening(addr[0]))

    async def _attr_listening(self, attr):
        while attr in self.attrs.values(): 
            attr_name, attr_type = attr.name, attr.type
            attr_value = attr.value
            async with attr.desc_changed: 
                await attr.desc_changed.wait()
                if attr.name != attr_name or attr.type != attr_type:
                    await self.send(f'attr {attr.attr_id} {attr.name} {attr.type_str()}')
                elif attr.value != attr_value:
                    await self.send(f'val {attr.attr_id} {attr.value}')
                async with self.attrs_changed:
                    self.attrs_changed.notify_all()

    async def _bus_listening(self, bus):
        while True:
            async with bus.packet_changed:
                if bus.packet is not None:
                    device_id, msg = bus.packet
                    await self.read_msg(msg)
                await bus.packet_changed.wait()

    async def read_msg(self, msg):
        async with self.msg_changed:
            self.msg = msg
            self.msg_changed.notify_all()
        words = msg.split()
        if re.match('\s*get\s+desc\s*', msg):
            await self.send(f'desc {self.name} {self.n_attr}')
        elif re.match('\s*get\s+attr\s+\d+\s*', msg):
            attr = self._find_attr(int(words[2]))
            if attr is not None:
                await self.send(f'attr {attr.attr_id} {attr.name} {attr.type_str()}')
        elif re.match('\s*get\s+val\s+\d+\s*', msg):
            attr = self._find_attr(int(words[2]))
            if attr is not None:
                await self.send(f'val {attr.attr_id} {attr.value}')

    async def send(self, msg):
        while True:
            if self.disconnected():
                async with self.desc_changed:
                    await self.desc_changed.wait() # wait for reconnection
            else:
                return await self.addr[0].send(0x42, msg)

    @property
    def n_attr(self):
        return len(self.attrs)

class RemoteDevice(Device):

    def __init__(self, *, addr=None, name=None, type='unknown'):
        super().__init__(addr=addr, name=name, type=type)
        self.n_attr = None
        self.create_task(self._desc_fetching())
        self.create_task(self._attrs_fetching())

    async def _desc_fetching(self):
        while True:
            if (self.name is None or self.n_attr is None) and not self.disconnected():
                logger.debug(f'{self}: incomplete desc') 
                await self.send(f'get desc')
                await asyncio.sleep(5)
            else:
                await self.changed.wait()

    async def _attrs_fetching(self):
        while True:
            if self.n_attr is None:
                await self.changed.wait()
            else:
                if len(self.attrs) < self.n_attr:
                    logger.debug(f'{self}: fetching attrs') 
                    attr_ids = set(range(self.n_attr)) - self.attrs_ids
                    cs = {self.send(f'get attr {a_id}') for a_id in attr_ids}
                    await asyncio.gather(*cs)
                    await asyncio.sleep(5 * (len(cs) % 4))
                elif len(self.attrs) > self.n_attr:
                    attr_ids = self.attr_ids - set(range(self.n_attr))
                    logger.debug(f'{self}: too many attrs, removing {attr_ids}') 
                    for attr_id in attr_ids: 
                        self.remove_attr(attr_id)
                else:
                    await self.changed.wait()

    async def _attr_fetching(self, attr):
        while attr in self.attrs.values():
            if (attr.name is None or attr.type is None) and attr.attr_id is not None:
                logger.debug(f'{attr} has incomplete desc')
                await self.send(f'get attr {attr.attr_id}')
                await asyncio.sleep(5)
            elif attr.value is None and attr.attr_id is not None:
                logger.debug(f'{attr} has no value')
                await self.send(f'get val {attr.attr_id}')
                await asyncio.sleep(5)
            else:
                await self.changed.wait()

    def add_attr(self, attr):
        super().add_attr(attr)
        self.create_task(self._attr_fetching(attr))

    async def read_msg(self, msg):
        async with self.msg_changed:
            self.msg = msg
            self.msg_changed.notify_all()
        words = msg.split()
        logger.debug(f'{self}: reading message: {msg}')
        if re.match('\s*desc\s+\w*\s+\d+\s*', msg):
            async with self.desc_changed:
                logger.debug(f'{self}: setting desc from msg')
                name, n_attr = words[1], int(words[2]) 
                if self.name != name or self.n_attr != n_attr:
                    self.desc_changed.notify_all()
                self.name, self.n_attr = name, n_attr 
        elif re.match('\s*attr\s+\d+\s+\w+\s+\w+\s*', msg):
            logger.debug('{self}: setting attribute\'s desc')
            attr_id, name, type = int(words[1]), words[2], words[3]
            attr = self._find_attr(attr_id, name)
            if attr is None:
                logger.debug(f'{self}: no attribute with id {attr_id}, creating one')
                attr = Attribute(type, attr_id=attr_id, name=name)
                async with self.attrs_changed:
                    self.add_attr(attr)
                    self.attrs_changed.notify_all()
            else:
                async with attr.desc_changed:
                    attr.desc_changed.notify_all()
                    attr.attr_id, attr.name, attr.type = attr_id, name, type
        elif re.match('\s*val\s+\d+\s+\w+\s*', msg):
            logger.debug(f'{self}: setting attribute\'s value')
            attr_id, value = int(words[1]), words[2]
            attr = self._find_attr(attr_id)
            if attr is None:
                logger.debug(f'{self}: failed to find attribute with id {attr_id}')
                await self.send(f'get attr {attr.attr_id}')
            else:
                async with attr.desc_changed:
                    attr.value = value
                    attr.desc_changed.notify_all()

    async def send(self, msg):
        while True:
            if self.disconnected():
                async with self.desc_changed:
                    await self.desc_changed.wait() # wait for reconnection
            else:
                return await self.addr[0].send(self.addr[1], msg)

    def disconnected(self):
        if self.addr is None:
            return True
        return False

class Attribute(Node):

    def __init__(self, type=None, value=None, *, attr_id=None, name=None):
        super().__init__()
        self.attr_id = attr_id
        self.name = name
        self.type = type 
        self.value = value 
        self.desc_changed = self.Condition()

    def __str__(self):
        if self.name is not None:
            return f'attribute "{self.name}"'
        elif self.attr_id is not None:
            return f'attribute [{self.attr_id}]'
        else:
            return 'attribute'

    def type_str(self):
        if self.type is int:
            return 'int'
        if self.type is float:
            return 'float'
        if self.type is bool:
            return 'bool'
        if self.type is str:
            return 'str'

    @property
    def value(self):
        if self._value is None:
            return None
        if self.type == 'int':
            return int(self._value)
        if self.type == 'bool':
            return bool(float(self._value))
        return self._value

    @value.setter
    def value(self, value):
        self._value = value

