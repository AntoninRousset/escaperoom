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

class UDPBus(Bus):

    def __init__(self, path):
        super().__init__()
        self.path = path
        self.create_task(self._listener())
        self.sending = self.Condition()

    def __str__(self):
        return f'UDP [{self.path}]'

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
                        logger.debug(f'{self}: Reading packet: {bus.packet}') 
                        self.packet = (addr, msg) 
                        self.packet_changed.notify_all()
                        await self.read_msg(addr, msg)
                logger.debug(f'{self}: Waiting for bus packet')
                await bus.packet_changed.wait()

    def _find_device(self, addr=None, name=None):
        for device in self.devices.values():
            if not device.disconnected() and device.addr == addr:
                return device
            elif device.name == name:
                return device

    async def read_msg(self, dest, msg): 
        if re.match('\s*desc\s+\w+\s+\w+\s*', msg):
            name = msg.split()[1]
            device = self._find_device(dest, name)
            if device is None:
                logger.debug(f'{self}: no device with addr: {dest}')
                device = Device(addr=dest, name=name)
                async with self.devices_changed:
                    self.add_device(device)
                    self.devices_changed.notify_all()
            else:
                logger.debug(f'{self}: found device with addr: {dest}')
                async with device.desc_changed:
                    if device.addr != dest or device.name != name:
                        device.desc_changed.notify_all()
                    device.addr, device.name = dest, name
        device = self._find_device(dest)
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

    async def _attr_listening(self, attr):
        while attr in self.attrs.values(): 
            async with attr.desc_changed: 
                await attr.desc_changed.wait()
                async with self.attrs_changed:
                    self.attrs_changed.notify_all()

    def add_attr(self, attr):
        uid = hex(id(attr)) 
        self.attrs[uid] = attr
        self.create_task(self._attr_listening(attr))
        logger.debug(f'{self}: {attr} added')

    async def remove_attr(self, attr_id, name):
        async with self.attrs_changed:
            for uid, attr in self.attrs.items():
                if attr.name == name:
                    return self.attrs.remove(uid)
                elif attr.attr_id == attr_id:
                    return self.attrs.remove(uid)

    async def send(self, msg):
        while True:
            if self.disconnected():
                async with self.desc_changed:
                    await self.desc_changed.wait() # wait for reconnection
            else:
                return await self.addr[0].send(self.addr[1], msg)

    def _find_attr(self, attr_id=None, name=None):
        for attr in self.attrs.values():
            if name is not None and attr.name == name:
                return attr
            elif attr.attr_id == attr_id:
                return attr

    @property
    def attrs_ids(self):
        return {a.attr_id for a in self.attrs.values() if a.attr_id is not None}

class LocalDevice(Device):

    def __init__(self, *, addr, name, type='unknown'):
        super().__init__(addr=addr, name=name, type=type)

    async def read_msg(self, addr, msg):
        async with self.msg_changed:
            self.msg = msg
            self.msg_changed.notify_all()
        words = msg.split()
        if re.match('\s*get\s+desc\s*', msg):
            await self.send(f'desc {self.name} {self.n_attr}')
        elif re.match('\s*get\s+attr\s+\d+\s*', msg):
            attr = self._find_attr(int(words[2]))
            if attr is not None:
                await self.send(f'attr {attr.attr_id} {attr.name} {attr.type}')
        elif re.match('\s*get\s+val\s+\d+\s*'):
            attr = self._find_attr(int(words[2]))
            if attr is not None:
                await self.send(f'val {attr.attr_id} {attr.value}')

    @property
    def n_attr(self):
        return len(self.attrs)

class RemoteDevice(Device):

    def __init__(self, *, addr=None, name=None, type='unknown'):
        super().__init__(addr=addr, name=name, type=type)
        self.n_attr = None
        self.create_task(self._desc_fetching())
        self.create_task(self._attrs_fetching())

    def __str__(self):
        if self.name is not None:
            return f'device "{self.name}"'
        elif not self.disconnected():
            return f'device {self.addr[1]}@{self.addr[0]}'
        else:
            return 'device'

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
                logger.debug(f'attribute {attr} has incomplete desc')
                await self.send(f'get attr {attr.attr_id}')
                await asyncio.sleep(5)
            elif attr.value is None and attr.attr_id is not None:
                logger.debug(f'attribute {attr} has no value')
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
                logger.debug('device: Set desc from msg')
                name, n_attr = words[1], int(words[2]) 
                if self.name != name or self.n_attr != n_attr:
                    self.desc_changed.notify_all()
                self.name, self.n_attr = name, n_attr 
        elif re.match('\s*attr\s+\d+\s+\w+\s+\w+\s*', msg):
            logger.debug('device: setting attribute\'s desc')
            attr_id, name, type = int(words[1]), words[2], words[3]
            attr = self._find_attr(attr_id, name)
            if attr is None:
                logger.debug(f'Device: Attr {attr_id} non existant, creating one')
                attr = Attribute(type, attr_id=attr_id, name=name)
                async with self.attrs_changed:
                    self.add_attr(attr)
                    self.attrs_changed.notify_all()
            else:
                async with attr.desc_changed:
                    attr.desc_changed.notify_all()
                    attr.attr_id, attr.name, attr.type = attr_id, name, type
        elif re.match('\s*val\s+\d+\s+\w+\s*', msg):
            logger.debug('device: setting attribute\'s value')
            attr_id, value = int(words[1]), words[2]
            attr = self._find_attr(attr_id)
            if attr is None:
                logger.debug(f'{self}: non existant "{attr}"')
                await self.send(f'get attr {attr.attr_id}')
            else:
                async with attr.desc_changed:
                    attr.value = value
                    attr.desc_changed.notify_all()

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

