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
from ..utils import ensure_iter


class NotReady(Exception):
    pass


class Device(Network):

    _downloadings = defaultdict(asyncio.Lock)

    class Attribute():

        @classmethod
        def convert(cls, value, type):
            if value is None:
                return None
            if type is None:
                return value
            if type == 'bool':
                if isinstance(value, str):
                    if re.match('((T|t)rue|(O|o)n|(Y|y)es)', value):
                        return True
                    elif re.match('((F|f)alse|(O|o)ff|(N|n)o)', value):
                        return False
                    return bool(float(value))
                else:
                    return bool(value)
            if type == 'int':
                return int(value)
            if type == 'float':
                return float(value)
            if type == 'str':
                return str(value)
            raise ValueError()

        def __init__(self, name=None, type=None, value=None):
            super().__init__()
            self.name = name
            self.type = type
            self._value = value

        def __str__(self):
            if self.name is not None and self.value is not None:
                return f'attribute "{self.name}" [{self.value}]'
            return 'attribute'

        @property
        def value(self):
            return self._value

        @value.setter
        def value(self, value):
            self._value = Device.Attribute.convert(value, self.type)

    def __init__(self, name, *, desc=None, type='unknown', tasks={},
                 reset=False):
        super().__init__(name, desc)
        self._attrs = None
        self._connected = asyncio.Event()
        self.type = type
        self.loc = None
        self.add_tasks(tasks)
        #if reset: asyncio.create_task(self.reset()) #TODO?

    def add_tasks(self, tasks):

        async def task_wrapper(task):
            try:
                await task(self)
            except BaseException:
                self._logger.exception(f'{self} task {task} failed')

        for task in ensure_iter(tasks):
            asyncio.create_task(task_wrapper(task))

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

    async def _set_value(self, name, value, *, type=None):
        try:
            attr = self._find_attr(name)
            if type is not None:
                attr.type = type
            attr.value = value
        except (KeyError, AttributeError):
            if self._attrs is None:
                self._attrs = set()
            self._attrs.add(Device.Attribute(name, type=type,
                                             value=value))

    def get_value(self, name):
        return self._find_attr(name).value

    async def set_value(self, name, value):
        async with self.changed:
            await self._set_value(name, value)
            self.changed.notify_all()
            await asyncio.sleep(0)  # TODO? remove

    @property
    def n_attr(self):
        if self._attrs is None:
            return None
        return len(self._attrs)

    @property
    def ready(self):
        return self._attrs is not None


def device(name=None, *args, **kwargs):
    def decorator(func):
        d = Device.find_entry(name)
        if d is not None:
            return d
        return Device(name, tasks={func}, *args, **kwargs)
    return decorator


import etcd3_asyncio as etcd

# Lease every values ? maybe not
# For reboot let's del every key and every node are responsible to repopulate
class EtcdDevice(Device):

    def __init__(self, name, *args, **kwargs):
        super().__init__(name, *args, **kwargs)
        self._path = f'/devices/{name}/'.encode()

        self._watching = asyncio.Event()
        asyncio.create_task(self.__watcher())

    async def __watcher(self):
        async for event in etcd.Watch(self._path, filters=['nodelete']):
            await self._download()
            self._watching.set()

    async def _download(self):
        attrs = await etcd.Range(self._path)
        async with self.changed:
            for path, data in attrs.items():
                name = path.rsplit(b'/', 1)[-1].decode()
                words = data.decode().split(maxsplit=1)
                try:
                    type, value = words
                except ValueError:
                    type, value = words[0], ''
                try:
                    attr = self._find_attr(name)
                    attr.type = type
                    attr.value = value
                except (KeyError, AttributeError):
                    if self._attrs is None:
                        self._attrs = set()
                    self._attrs.add(Device.Attribute(name, type=type,
                                                     value=value))
            self.changed.notify_all()

    async def _set_value(self, name, value, *, type=None):
        key = self._path + name.encode()

        if type is None:
            data = await etcd.Get(key, default=b'str')
            type = data.split()[0].decode()

        value = Device.Attribute.convert(value, type)
        await etcd.Put(key, f'{type} {value}'.encode())

        # TODO, prevent changing type while setting value

        while True:
            try:
                attr = self._find_attr(name)
                if attr is not None:
                    if attr.value == value:
                        return
            except (KeyError, AttributeError):
                pass
            await self.changed.wait()

    async def set_value(self, name, value):
        await self._watching.wait()
        async with self.changed:
            await self._set_value(name, value)
            self.changed.notify_all()


def etcd_device(name=None, *args, **kwargs):
    def decorator(func):
        d = EtcdDevice.find_entry(name)
        if d is not None:
            return d
        return EtcdDevice(name, tasks={func}, *args, **kwargs)
    return decorator


class SerialDevice(Device):

    discover = False
    _buses = set()

    class Addr():

        def __init__(self, bus, device_id):
            self.bus = bus
            self.device_id = device_id

        def __eq__(self, other):
            if other is None:
                return False
            if self.bus is None or other.bus is None:
                return False
            if self.bus != other.bus:
                return False
            if self.device_id is None or other.device_id is None:
                return False
            if self.device_id != other.device_id:
                return False
            return True

        def __str__(self):
            return f'0x{self.device_id:02x}@{self.bus}'

    @classmethod
    def _find_device(cls, addr):
        for device in cls.entries():
            try:
                if device.addr.bus == addr.bus \
                   and device.addr.device_id == addr.device_id:
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
        if re.match(r'\s*desc\s+\w+\s+\w+\s*', msg):
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
                        await asyncio.sleep(0)
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
        self._has_reset = asyncio.Event()
        self.addr = None
        if reset:
            asyncio.create_task(self.__reset_before_start())

    async def __reset_before_start(self):
        await self.reset()
        asyncio.create_task(self._desc_fetching())
        asyncio.create_task(self._attrs_fetching())

    async def _desc_fetching(self):
        while True:
            if self.name is None or self._attrs is None:
                self._log_debug(f'incomplete desc')
                await self._send(f'get desc')
                await asyncio.wait({asyncio.sleep(10), self._has_reset.wait()},
                                   return_when=asyncio.FIRST_COMPLETED)
            else:
                async with self.changed:
                    await self.changed.wait()

    async def _attrs_fetching(self):
        while True:
            async with self.changed:
                if self.n_attr is None:
                    await self.changed.wait()
                    continue
            cos = set()
            for attr_id, attr in zip(range(self.n_attr), self._attrs):
                if attr.name is None or attr.type is None:
                    cos.add(self._send(f'get attr {attr_id}'))
                elif attr._value is None:
                    cos.add(self._send(f'get val {attr_id}'))
            if cos:
                self._log_debug(f'incomplete attrs') 
                await asyncio.gather(*cos)
                await asyncio.wait({asyncio.sleep(10), self._has_reset.wait()},
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
        if re.match(r'\s*desc\s+\w*\s+\d+\s*', msg):
            self._log_debug(f'setting desc from msg')
            name, n_attr = words[1], int(words[2])
            if self.name != name or self.n_attr != n_attr:
                async with self.changed:
                    self.name = name
                    self._set_n_attr(n_attr)
                    self.changed.notify_all()
                    await asyncio.sleep(0)
        elif re.match(r'\s*attr\s+\d+\s+\w+\s+\w+\s*', msg):
            if self._attrs is not None:
                self._log_debug(f'setting attribute from msg')
                attr = self._attrs[int(words[1])]
                name, type, val = words[2], words[3], words[4]
                if attr.name != name or attr.type != type or attr.value != val:
                    async with self.changed:
                        attr.name, attr.type, attr.value = name, type, val
                        self.changed.notify_all()
                        await asyncio.sleep(0)
        elif re.match(r'\s*val\s+\d+\s+\w+\s*', msg):
            if self._attrs is not None:
                self._log_debug(f'setting attribute\'s value from msg')
                attr_id, value = int(words[1]), words[2]
                attr = self._attrs[attr_id]
                if attr._value != value:
                    async with self.changed:
                        attr.value = value
                        self.changed.notify_all()
                        await asyncio.sleep(0)

    async def _send(self, msg):
        await self._connected.wait()
        return await self.addr.bus.send(self.addr.device_id, msg)

    async def _find_attr_wait(self, name):
        repeat = True
        while repeat:
            repeat = False
            while self._attrs is None:
                await self.changed.wait()
            for attr_id, attr in zip(range(self.n_attr), self._attrs):
                if attr.name == name:
                    return attr_id, attr
                elif attr.name is None:
                    repeat = True
            await self.changed.wait()
        raise KeyError(f'Non existent attribute "{name}"')

    def _find_attr_nowait(self, name):
        if self._attrs is None:
            raise NotReady('device is not ready')
        for attr_id, attr in zip(range(self.n_attr), self._attrs):
            if attr.name == name:
                return attr_id, attr
            elif attr.name is None:
                raise NotReady('attribute is not ready')
        raise KeyError(f'Non existent attribute "{name}"')

    def get_value(self, name):
        try:
            _, attr = self._find_attr_nowait(name)
            if attr.value is None: raise NotReady('attribute not ready')
        except NotReady: raise
        except KeyError as e:
            self._log_warning(f'cannot get value: {e}')
            raise
        return attr.value

    async def _set_value(self, name, value, *, force=False):
        while True:
            try:
                attr_id, attr = await self._find_attr_wait(name)
                value = Device.Attribute.convert(value, attr.type)
                if attr._value == value and not force:
                    return
                await self._send(f'set val {attr_id} {value}')
                while attr._value != value:
                    await asyncio.wait_on_condition(self.changed, timeout=5)
                return
            except TimeoutError:
                self._log_warning('cannot set value: attribute did not change')
            except KeyError as e:
                self._log_warning(f'cannot set value: {e}')
                if not self.changed.locked():
                    await self.changed.acquire() #TODO, how to do it?
                raise
            except Exception as e:
                print('unhandled exception:', repr(e))
            print('retry')

    async def reset(self):
        await self._send(f'reset')
        async with self.changed:
            self._attrs = None
            self._has_reset.set()
            self._has_reset.clear()
            self.changed.notify_all()
            await asyncio.sleep(0)

    @property
    def ready(self):
        if not super().ready:
            return False
        if self.addr is None:
            return False
        for attr in self._attrs:
            if attr.name is None or attr.type is None or attr.value is None:
                return False
        return True

