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

    _group = dict()
    devices_changed = asyncio.Condition()

    class Attribute():

        def __init__(self, name, type=None, value=None, *, attr_id=None):
            super().__init__()
            self.attr_id = attr_id
            self.name = name
            self.type = type
            self.value = value
            self.desc_changed = asyncio.Condition()

        def __str__(self):
            name = f'"{self.name}"' if self.name is not None else '???'
            attr_id = self.attr_id if self.attr_id is not None else '?'
            return f'attribute {name} [{attr_id}]'

        @property
        def value(self):
            if self._value is None:
                return None
            return {'int': int, 'float': float, 'str': str,
                    'bool': (lambda x: bool(float(x)))}(self._value)

        @value.setter
        def value(self, value):
            self._value = value

    def __init__(self, name, *, addr=None, type='?'):
        super().__init__(name)
        self.addr = addr
        self.type = type
        self.n_attr = None
        self.desc_changed = self.Condition()
        self.msg = None
        self.msg_changed = self.Condition()
        self.attrs = dict()
        self.attrs_changed = self.Condition()
        self._register()

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
        _id = hex(id(attr))
        self.attrs[_id] = attr
        self.create_task(self._attr_listening(attr))
        self._log_debug(f'{self}: {attr} added')

    def create_attr(self, *args, **kwargs):
        attr = Device.Attribute(*args, **kwargs)
        self.add_attr(attr)
        return attr

    async def read_msg(self, msg):
        pass

    async def remove_attr(self, attr_id, name):
        async with self.attrs_changed:
            for id, attr in self.attrs.items():
                if attr.name == name:
                    return self.attrs.remove(id)
                elif attr.attr_id == attr_id:
                    return self.attrs.remove(id)

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
        if re.match(r'\s*get\s+desc\s*', msg):
            await self.send(f'desc {self.name} {self.n_attr}')
        elif re.match(r'\s*get\s+attr\s+\d+\s*', msg):
            attr = self._find_attr(int(words[2]))
            if attr is not None:
                await self.send(f'attr {attr.attr_id} {attr.name} {attr.type}')
        elif re.match(r'\s*get\s+val\s+\d+\s*', msg):
            attr = self._find_attr(int(words[2]))
            if attr is not None:
                await self.send(f'val {attr.attr_id} {attr.value}')

    async def send(self, msg):
        while True:
            if self.disconnected():
                async with self.desc_changed:
                    # wait for reconnection
                    await self.desc_changed.wait()
            else:
                return await self.addr[0].send(self.addr[1], msg)

    async def set_value(self, name, value):
        self._log_warning('set_value not implemented for remote device')
        raise RuntimeError

    def add_attr(self, attr):
        if attr.attr_id is None:
            attr.attr_id = len(self.attrs)
        super().add_attr(attr)

    @property
    def n_attr(self):
        return len(self.attrs)


class RemoteDevice(Device):

    def __init__(self, name, *, addr=None, type='?'):
        super().__init__(addr=addr, name=name, type=type)
        self.n_attr = None
        self.create_task(self._desc_fetching())
        self.create_task(self._attrs_fetching())

    async def _desc_fetching(self):
        while True:
            if (self.name is None or self.n_attr is None) and not self.disconnected():
                self._log_debug(f'{self}: incomplete desc')
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
                    self._log_debug(f'{self}: fetching attrs')
                    attr_ids = set(range(self.n_attr)) - self.attrs_ids
                    cs = {self.send(f'get attr {a_id}') for a_id in attr_ids}
                    await asyncio.gather(*cs)
                    await asyncio.sleep(5 * (len(cs) % 4))
                elif len(self.attrs) > self.n_attr:
                    attr_ids = self.attr_ids - set(range(self.n_attr))
                    self._log_debug(f'{self}: too many attrs, removing {attr_ids}') 
                    for attr_id in attr_ids:
                        self.remove_attr(attr_id)
                else:
                    await self.changed.wait()

    async def _attr_fetching(self, attr):
        while attr in self.attrs.values():
            if (attr.name is None or attr.type is None) and attr.attr_id is not None:
                self._log_debug(f'{attr} has incomplete desc')
                await self.send(f'get attr {attr.attr_id}')
                await asyncio.sleep(5)
            elif attr.value is None and attr.attr_id is not None:
                self._log_debug(f'{attr} has no value')
                await self.send(f'get val {attr.attr_id}')
                await asyncio.sleep(5)
            else:
                await self.changed.wait()

    async def set_value(self, name, value):
        async def get_sane_attr(name):
            while True:
                attr = self._find_attr(name=name)
                if attr is not None:
                    break
                await asyncio.sleep(1)
            while attr.type is None or attr.value is None:
                await asyncio.sleep(1)
            return attr

        attr = await asyncio.wait_for(get_sane_attr(name), timeout=30)
        msg_value = str(value)
        # Not good
        if attr.type == 'bool':
            if value == 'True' or value == 'true':
                msg_value = '1'
            elif value == 'False' or value == 'false':
                msg_value = '0'
        async with attr.desc_changed:
            await self.send(f'set val {attr.attr_id} {msg_value}')
            while str(attr.value) != str(value):
                await attr.desc_changed.wait()

    def add_attr(self, attr):
        super().add_attr(attr)
        self.create_task(self._attr_fetching(attr))

    async def read_msg(self, msg):
        async with self.msg_changed:
            self.msg = msg
            self.msg_changed.notify_all()
        words = msg.split()
        self._log_debug(f'{self}: reading message: {msg}')
        if re.match(r'\s*desc\s+\w*\s+\d+\s*', msg):
            async with self.desc_changed:
                self._log_debug(f'{self}: setting desc from msg')
                name, n_attr = words[1], int(words[2]) 
                if self.name != name or self.n_attr != n_attr:
                    self.desc_changed.notify_all()
                self.name, self.n_attr = name, n_attr 
        elif re.match(r'\s*attr\s+\d+\s+\w+\s+\w+\s*', msg):
            self._log_debug(f'{self}: setting attribute\'s desc')
            attr_id, name, type = int(words[1]), words[2], words[3]
            attr = self._find_attr(attr_id, name)
            if attr is None:
                self._log_debug(f'{self}: no attribute with id {attr_id}, creating one')
                attr = Device.Attribute(name, type, attr_id=attr_id)
                async with self.attrs_changed:
                    self.add_attr(attr)
                    self.attrs_changed.notify_all()
            else:
                async with attr.desc_changed:
                    attr.desc_changed.notify_all()
                    attr.attr_id, attr.name, attr.type = attr_id, name, type
        elif re.match(r'\s*val\s+\d+\s+\w+\s*', msg):
            self._log_debug(f'{self}: setting attribute\'s value')
            attr_id, value = int(words[1]), words[2]
            attr = self._find_attr(attr_id)
            if attr is None:
                self._log_debug(f'{self}: failed to find attribute with id {attr_id}')
                await self.send(f'get attr {attr.attr_id}')
            else:
                async with attr.desc_changed:
                    attr.value = value
                    attr.desc_changed.notify_all()

    async def send(self, msg):
        while True:
            if self.disconnected():
                async with self.desc_changed:
                    # wait for reconnection
                    await self.desc_changed.wait()
            else:
                return await self.addr[0].send(self.addr[1], msg)

    def disconnected(self):
        if self.addr is None:
            return True
        return False
