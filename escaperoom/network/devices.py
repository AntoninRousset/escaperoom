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

from . import asyncio, Network


class Device(Network):

    _group = Network.Group()

    class Attribute():

        def __init__(self, name=None, type=None, value=None):
            super().__init__()
            self.name = name
            self.type = type 
            self._value = value 

        def __str__(self):
            if self.name is not None and value is not None:
                return f'attribute "{self.name}" [{self.value}]'
            return 'attribute'

        @property
        def value(self):
            if self._value is None:
                return None
            if self.type == 'int':
                return int(self._value)
            if self.type == 'float':
                return float(self._value)
            if self.type == 'bool':
                return bool(float(self._value))
            if self.type == 'str':
                return str(self._value)
            return self._value

        @value.setter
        def value(self, value):
            self._value = value


    def __init__(self, name, *, type='unknown'): 
        super().__init__(name)
        if self._first_init:
            self._attrs = None
            self.sane = asyncio.Event()
        self.type = type

    def __str__(self):
        return 'device' if self.name is None else f'device "{self.name}"'


class SerialDevice(Device):

    discover = False
    _buses = set()
    buses_changed = asyncio.Event()

    class Addr():

        def __init__(self, bus, device_id):
            self.bus = bus
            self.device_id = device_id

        def __str__(self):
            return f'0x{self.device_id:02x}@{self.bus}'


    @classmethod
    def _find_device(cls, addr):
        for device in cls.nodes():
            try:
                if (device.addr.bus == addr.bus and
                    device.addr.device_id == addr.device_id):
                    return device
            except AttributeError:
                pass

    @classmethod
    async def _device_radar(cls, bus):
        def lost_device():
            for device in cls.nodes():
                try:
                    if device.addr is None:
                        return True
                except AttributeError:
                    pass
        async def safe_broadcast(bus):
            try:
                await bus.broadcast('get desc')
            except Exception as e:
                cls._logger.warning(f'cannot broadcast on {bus}: {e}')
        while True:
            if cls.discover or lost_device():
                await asyncio.gather(*(safe_broadcast(bus) for bus in cls._buses))
                await asyncio.sleep(5)
            else:
                await cls.group_changed.wait()

    @classmethod
    async def _bus_listening(cls, bus):
        while bus in cls._buses:
            async with bus.packet_changed:
                if bus.packet is not None:
                    device_id, msg = bus.packet
                    addr = SerialDevice.Addr(bus, device_id)
                    cls._logger.debug(f'reading msg "{msg}"')
                    if re.match('\s*desc\s+\w+\s+\w+\s*', msg):
                        name = msg.split()[1]
                        device = Device.find_node(name)
                        if device is None:
                            cls._logger.debug(f'no device "{name}"')
                            if cls.discover:
                                cls._logger.debug(f'creating device "{name}"')
                                SerialDevice(name, addr=addr)
                        elif isinstance(device, SerialDevice):
                            async with device.changed:
                                device.addr = addr
                                device.changed.notify_all()
                    device = cls._find_device(addr)
                    if device is None:
                        if cls.discover:
                            cls._logger.warning(f'could not find device for {addr}')
                    else:
                        try:
                            await device._read_msg(msg)
                        except Exception as e:
                            cls._logger.warning(f'{device}: failed to read msg '
                                                f'"{msg}": {e}')
                await bus.packet_changed.wait()

    @classmethod
    def add_bus(cls, bus):
        if bus not in cls._buses:
            asyncio.create_task(cls._bus_listening(bus))
            asyncio.create_task(cls._device_radar(bus))
            cls._buses.add(bus)
        cls._logger.debug(f'{bus} added')

    def __init__(self, name, *, addr=None, type='unknown'):
        super().__init__(name, type=type)
        if self._first_init:
            self.create_task(self._desc_fetching())
            self.create_task(self._attrs_fetching())
        self.addr = addr

    async def _desc_fetching(self):
        while True:
            if ((self.name is None or self._attrs is None) and
                 self.addr is not None):
                self._log_debug(f'incomplete desc') 
                await self._send(f'get desc')
                await asyncio.sleep(5)
            else:
                await self.changed.wait()

    async def _attrs_fetching(self):
        while True:
            if self.n_attr is None or self.addr is None:
                async with self.changed:
                    await self.changed.wait()
            else:
                cos = set()
                for attr_id, attr in zip(range(self.n_attr), self._attrs):
                    if attr.name is None or attr.type is None:
                        cos.add(self._send(f'get attr {attr_id}'))
                    if attr._value is None:
                        cos.add(self._send(f'get val {attr_id}'))
                if cos:
                    await asyncio.gather(*cos)
                    await asyncio.sleep(5)
                else:
                    async with self.changed:
                        await self.changed.wait()

    def _set_n_attr(self, value):
        if value is None: self._attrs = None
        elif self._attrs is None: self._attrs = list()
        for i in range(value-len(self._attrs)):
            self._attrs.append(Device.Attribute())
        (self._attrs.pop() for i in range(len(self._attrs)-value))

    async def _read_msg(self, msg):
        words = msg.split()
        self._log_debug(f'reading message: {msg}')
        if re.match('\s*desc\s+\w*\s+\d+\s*', msg):
            self._log_debug(f'setting desc from msg')
            name, n_attr = words[1], int(words[2]) 
            if self.name != name or self.n_attr != n_attr:
                async with self.changed:
                    self.name = name
                    self._set_n_attr(n_attr)
                    self.changed.notify_all()
        elif re.match('\s*attr\s+\d+\s+\w+\s+\w+\s*', msg):
            self._log_debug(f'setting attribute from msg')
            attr_id, name, type = int(words[1]), words[2], words[3]
            attr = self._attrs[attr_id]
            if attr.name != name or attr.type != type:
                async with self.changed:
                    attr.name, attr.type = name, type
                    self.changed.notify_all()
        elif re.match('\s*val\s+\d+\s+\w+\s*', msg):
            self._log_debug(f'setting attribute\'s value from msg')
            attr_id, value = int(words[1]), words[2]
            attr = self._attrs[attr_id]
            if attr._value != value:
                async with self.changed:
                    attr.value = value
                    self.changed.notify_all()

    async def _send(self, msg):
        while self.addr is None:
            async with self.changed:
                await self.changed.wait()
        return await self.addr.bus.send(self.addr.device_id, msg)

    async def _find_attr(self, name):
        repeat = True
        while repeat:
            repeat = False
            async with self.changed:
                for attr in self._attrs:
                    if attr.name == name: return attr
                    elif attr.name is None: repeat = True
                self.changed.wait()
        raise KeyError()

    async def get_value(self, name):
        attr = await self._find_attr(name)
        while attr.value is None:
            async with self.changed:
                self.changed.wait()
            return attr.value

    async def set_value(self, name, value):
        attr = await self._find_attr(name)
        async with self.changed:
            await self._send(f'set val {attr.attr_id} {attr.to_str(value)}')
            while attr.value != value:
                await attr.changed.wait()

    @property
    def n_attr(self):
        if self._attrs is None: return None
        return len(self._attrs)

'''
class LocalDevice(Device):

    def __init__(self, name, *, bus, addr, type='?'):
        super().__init__(name=name, addr=(bus, addr), type=type)
        self.create_task(self._bus_listening(bus))

    async def _attr_listening(self, attr):
        while attr in self.attrs.values(): 
            attr_name, attr_type = attr.name, attr.type
            attr_value = attr.value
            async with attr.desc_changed: 
                await attr.desc_changed.wait()
                if attr.name != attr_name or attr.type != attr_type:
                    await self.send(f'attr {attr.attr_id} {attr.name} {attr.type}')
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
                await self.send(f'attr {attr.attr_id} {attr.name} {attr.type}')
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
                return await self.addr[0].send(self.addr[1], msg)

    async def set_value(self, name, value):
        self._log_warning('set_value not implemented for local device')
        raise RuntimeError

    def add_attr(self, attr):
        if attr.attr_id is None:
            attr.attr_id = len(self.attrs)
        super().add_attr(attr)

    @property
    def n_attr(self):
        return len(self.attrs)
'''
