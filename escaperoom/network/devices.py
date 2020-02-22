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

import aiohttp, json, re
from aiohttp_sse_client import client as sse_client
from collections import defaultdict

from . import asyncio, Network


class NotReady(Exception):
    pass

class Device(Network):

    _downloadings = defaultdict(asyncio.Lock)

    class Attribute():

        def __init__(self, name=None, type=None, value=None): 
            super().__init__()
            self.name = name
            self.type = type 
            self._value = value 

        def __str__(self):
            if self.name is not None and self.value is not None:
                return f'attribute "{self.name}" [{self.value}]'
            return 'attribute'

        def convert(self, value, type=None):
            value = str(value)
            if type is None:
                type = self.type
            if type == 'bool':
                if re.match('((T|t)rue|(O|o)n|(Y|y)es)', value): return '1'
                elif re.match('((F|f)alse|(O|o)ff|(N|n)o)', value): return '0' 
                else: return value
            return value

        @property
        def value(self):
            try:
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
            except ValueError:
                return None

        @value.setter
        def value(self, value):
            self._value = self.convert(value)

    @classmethod
    async def _download_device(cls, host, id):
        async def fetch(loc):
            while True:
                try:
                    async with aiohttp.ClientSession() as session:
                        async with session.get(loc) as resp:
                            return await resp.json()
                except aiohttp.ClientConnectorError:
                    await asyncio.sleep(1)
        loc = host+'/device?id='+id
        async with cls._downloadings[loc]:
            data = await fetch(loc)
            device = cls.find_entry(data['name'])
            if device is None:
                device = Device(data['name'], type=data['type'])
            if device.type is 'unknown':
                device.type = data['type']
            async with device.changed:
                if data['attrs'] is None and device._attrs is not None:
                    device._attrs = None
                    return device.changed.notify_all()
                elif data['attrs'] is not None and device._attrs is None:
                    device._attrs = list()
                    device.changed.notify_all()
                for i in range(0, len(data['attrs'])):
                    attr = data['attrs'][str(i)]
                    if len(device._attrs) <= i:
                        device._attrs.append(Device.Attribute(attr['name'],
                                                              attr['type'],
                                                              attr['value']))
                        device.changed.notify_all() 
                    else:
                        d_attr = device._attrs[i]
                        if ( d_attr.name != attr['name'] or
                             d_attr.type != attr['type'] or
                             d_attr.value != attr['value'] ):
                            device.changed.notify_all() 
                        d_attr.name = attr['name']
                        d_attr.type = attr['type']
                        d_attr.value = attr['value']

    @classmethod
    async def _download(cls, host):
        async def fetch(loc):
            while True:
                try:
                    async with aiohttp.ClientSession() as session:
                        async with session.get(loc) as resp:
                            return await resp.json()
                except aiohttp.ClientConnectorError:
                    await asyncio.sleep(1)
        loc = host+'/devices'
        async with cls._downloadings[loc]:
            data = await fetch(loc)
            for id in data['devices'].keys():
                asyncio.create_task(cls._download_device(host, id))
        
    @classmethod
    async def _HTTP_listener(cls, host):
        loc = host+'/events'
        warned = False
        while True:
            try:
                async with sse_client.EventSource(loc) as event_source:
                    async for event in event_source:
                        data = json.loads(event.data)
                        if ( data['type'] == 'update' and
                             data['url'] == '/devices' ):
                            asyncio.create_task(cls._download(host))
                warned = False
            except aiohttp.ClientConnectorError:
                if not warned:
                    cls._logger.warning(f'failed to connect to {host}')
                    warned = True
                await asyncio.sleep(1)

    @classmethod
    def bind(cls, host):
        asyncio.create_task(cls._download(host))
        asyncio.create_task(cls._HTTP_listener(host))

    def __init__(self, name, *, desc=None, type='unknown', tasks={},
                 reset=False): 
        super().__init__(name)
        self.desc = desc
        self._attrs = None
        self._connected = asyncio.Event()
        self.type = type
        self._register(Device)
        #if reset: asyncio.create_task(self.reset()) #TODO
        {asyncio.create_task(task(self)) for task in tasks}

    def __str__(self):
        return f'device "{self.name}"'

    def __bool__(self):
        return self.ready

    async def reset(self):
        pass

    def _find_attr(self, name):
        if self._attrs is not None:
            for attr in self._attrs:
                if attr.name == name:
                    return attr
        raise KeyError(f'Non existent attribute "{name}"')

    async def get_value(self, name):
        return self._find_attr(name).value

    async def _set_value(self, name, value, *, type=None):
        try:
            attr = self._find_attr(name)
        except KeyError:
            if self._attrs is None:
                self._attrs = set()
            self._attrs.add(Device.Attribute(name, type=type, value=value))
        else:
            attr.value = value

    async def set_value(self, name, value):
        async with self.changed:
            await self._set_value(name, value)
            self.changed.notify_all()

    @property
    def n_attr(self):
        if self._attrs is None: return None
        return len(self._attrs)

    @property
    def ready(self):
        return True


def device(name=None, *args, **kwargs):
    def decorator(func):
        d = Device.find_entry(name)
        if d is not None: return d
        return Device(name, tasks={func}, *args, **kwargs)
    return decorator

class SerialDevice(Device):

    discover = False
    _buses = set()

    class Addr():

        def __init__(self, bus, device_id):
            self.bus = bus
            self.device_id = device_id

        def __eq__(self, other):
            if other is None: return False
            if self.bus is None or other.bus is None: return False
            if self.bus != other.bus: return False
            if self.device_id is None or other.device_id is None: return False
            if self.device_id != other.device_id: return False
            return True

        def __str__(self):
            return f'0x{self.device_id:02x}@{self.bus}'


    @classmethod
    def _find_device(cls, addr):
        for device in cls.entries():
            try:
                if (device.addr.bus == addr.bus and
                    device.addr.device_id == addr.device_id):
                    return device
            except AttributeError:
                pass

    @classmethod
    async def _device_radar(cls, bus):
        def lost_device():
            for device in cls.entries():
                if not device._connected.is_set():
                    cls._logger.debug(f'lost device: {device}')
                    return True
        async def safe_broadcast(bus):
            try:
                await bus.broadcast('get desc')
            except Exception as e:
                cls._logger.warning(f'cannot broadcast on {bus}: {e}')
        while True:
            if cls.discover or lost_device():
                await asyncio.gather(*{safe_broadcast(b) for b in cls._buses})
                await asyncio.sleep(10)
            else:
                await cls.group_changed().wait()

    @classmethod
    async def _bus_listening(cls, bus):
        while bus in cls._buses:
            async with bus.packet_changed:
                try:
                    if bus.packet is not None:
                        await cls._read_packet(bus)
                except Exception as e:
                    cls._logger.warning(f'could not read packet: {e}')
                await bus.packet_changed.wait()

    @classmethod
    async def _read_packet(cls, bus):
        device_id, msg = bus.packet
        addr = SerialDevice.Addr(bus, device_id)
        cls._logger.debug(f'reading packet "{bus.packet}" from {bus}')
        if re.match('\s*desc\s+\w+\s+\w+\s*', msg):
            name = msg.split()[1]
            device = Device.find_entry(name)
            if device is None:
                cls._logger.debug(f'no device "{name}"')
                if cls.discover:
                    cls._logger.debug(f'creating device "{name}"')
                    device = SerialDevice(name)
                    device.addr = addr
            elif isinstance(device, SerialDevice):
                async with device.changed:
                    if device.addr != addr:
                        cls._logger.debug(f'device "{name}" found, addressing')
                        device.addr = addr
                        device._connected.set()
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

    @classmethod
    def add_bus(cls, bus):
        if bus not in cls._buses:
            asyncio.create_task(cls._bus_listening(bus))
            asyncio.create_task(cls._device_radar(bus))
            cls._buses.add(bus)
        cls._logger.debug(f'{bus} added')

    def __init__(self, name, *, desc=None, type='unknown', reset=False):
        super().__init__(name, desc=desc, type=type, reset=reset)
        self._reset = asyncio.Event()
        self.addr = None
        if reset: asyncio.create_task(self.__reset_before_start())
        self._register(SerialDevice)

    async def __reset_before_start(self):
        await self.reset()
        asyncio.create_task(self._desc_fetching())
        asyncio.create_task(self._attrs_fetching())

    async def _desc_fetching(self):
        while True:
            if self.name is None or self._attrs is None:
                self._log_debug(f'incomplete desc') 
                await self._send(f'get desc')
                await asyncio.wait({asyncio.sleep(10), self._reset.wait()},
                                   return_when=asyncio.FIRST_COMPLETED)
            else:
                async with self.changed:
                    await self.changed.wait()

    async def _attrs_fetching(self):
        while True:
            if self.n_attr is None:
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
                    self._log_debug(f'incomplete attrs') 
                    await asyncio.gather(*cos)
                    await asyncio.wait({asyncio.sleep(10), self._reset.wait()},
                                       return_when=asyncio.FIRST_COMPLETED)
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
            if self._attrs is not None:
                self._log_debug(f'setting attribute from msg')
                attr_id, name, type = int(words[1]), words[2], words[3]
                attr = self._attrs[attr_id]
                if attr.name != name or attr.type != type:
                    async with self.changed:
                        attr.name, attr.type = name, type
                        self.changed.notify_all()
        elif re.match('\s*val\s+\d+\s+\w+\s*', msg):
            if self._attrs is not None:
                self._log_debug(f'setting attribute\'s value from msg')
                attr_id, value = int(words[1]), words[2]
                attr = self._attrs[attr_id]
                if attr._value != value:
                    async with self.changed:
                        attr.value = value
                        self.changed.notify_all()

    async def _send(self, msg):
        await self._connected.wait()
        return await self.addr.bus.send(self.addr.device_id, msg)

    async def _find_attr(self, name, *, wait):
        repeat = True
        while repeat:
            repeat = False
            while self._attrs is None:
                if wait: await self.changed.wait()
                else: raise NotReady('device is not ready')
            for attr_id, attr in zip(range(self.n_attr), self._attrs):
                if attr.name == name: return attr_id, attr
                elif attr.name is None:
                    if wait: repeat = True
                    else: raise NotReady('attribute is not ready')
            if wait: await self.changed.wait()
        raise KeyError(f'Non existent attribute "{name}"')

    async def get_value(self, name):
        try:
            _, attr = await self._find_attr(name, wait=False)
            if attr.value is None: raise NotReady('attribute not ready')
        except NotReady: raise
        except KeyError as e:
            self._log_warning(f'cannot get value: {e}')
            raise
        return attr.value

    async def _set_value(self, name, value):
        async def wait_value(attr, value):
            while attr._value != value:
                await self.changed.wait()
        try:
            attr_id, attr = await self._find_attr(name, wait=True)
            value = attr.convert(value)
            await self._send(f'set val {attr_id} {value}')
            await asyncio.wait_for(wait_value(attr, value), timeout=60)
        except KeyError as e:
            self._log_warning(f'cannot set value: {e}')
            raise e
        except TimeoutError: 
            self._log_warning(f'cannot set value: the attribute did not change')
            raise e

    async def reset(self):
        await self._send(f'reset')
        async with self.changed:
            self._attrs = None
            self._reset.set()
            self._reset.clear()
            self.changed.notify_all()

    @property
    def ready(self):
        if self.addr is None or self._attrs is None: 
            return False
        for attr in self._attrs:
            if attr.name is None or attr.type is None or attr.value is None:
                return False
        return True

