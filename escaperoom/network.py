#!/usr/bin/env python

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

import asyncio
import PJON_daemon_client as pac
import re

import settings
from node import Node

if settings.testing == 'bus':
    from tests import bus_testing as testing
elif settings.testing == 'b3':
    from tests import b3_testing as testing

def com_debug(msg):
    if settings.com_debug:
        print(msg)

class Bus(Node):

    def __init__(self, path):
        super().__init__()
        self.path = path
        self.packet = None
        self.packet_changed = self.Condition()
        self.create_task(self._listener())
        self.sending = self.Condition()

    async def _listener(self):
        try:
            if settings.testing:
                async for p in testing.listen():
                    async with self.packet_changed:
                        com_debug(f'Bus: Received packet: (0x{p[0]:02x}, {p[1]})')
                        if p != self.packet_changed:
                            self.packet_changed.notify_all()
                        self.packet = p
            else:
                async for packet in pac.listen():
                    if isinstance(packet, pac.proto.PacketIngoingMessage):
                        device_id = packet.src
                        msg = packet.data.decode('ascii')
                        packet = (device_id, str(msg)[:-1])
                        async with self.packet_changed:
                            self.packet = packet
                            self.packet_changed.notify_all()
        except ConnectionRefusedError:
            print('ERROR: room disconnected -> please connect and restart')

    async def send(self, dest, msg):
        if settings.testing:
            if await testing.send(dest, msg):
                com_debug(f'Bus: Sent packet: (0x{dest:02x}, {msg})')
        else:
            async with self.sending:
                try:
                    result = await pac.send(dest, (msg).encode('ascii') + b'\0')
                    if result is pac.proto.OutgoingResult.SUCCESS:
                        com_debug(f'successful send to 0x{dest:02x}: {msg}')
                    else:
                        com_debug('********* PROBLEM')
                except ConnectionRefusedError:
                    print('ERROR: room disconnected')

    async def broadcast(self, msg):
        return await self.send(0x0, msg)

class Network(Node):

    def __init__(self):
        super().__init__()
        self.packet = None
        self.packet_changed = self.Condition()
        self.buses = dict()
        self.buses_changed = self.Condition()
        self.devices = dict()
        self.devices_changed = self.Condition()
        com_debug('Network: Created')

    async def _device_radar(self, bus):
        while bus in self.buses.values():
            try:
                await bus.broadcast('get desc')
            except Exception as e: 
                print(f'radar error: {e}')
            await asyncio.sleep(5)

    async def _bus_listening(self, bus):
        while bus in self.buses.values(): 
            async with bus.packet_changed:
                if bus.packet is not None:
                    device_id, msg = bus.packet
                    addr = (bus, device_id) 
                    async with self.packet_changed:
                        com_debug(f'Network: Read bus packet: {bus.packet}') 
                        self.packet = (addr, msg) 
                        self.packet_changed.notify_all()
                        await self.read_packet(self.packet)
                com_debug('Network: Waiting for new bus packet')
                await bus.packet_changed.wait()

    async def read_packet(self, packet): 
        addr, msg = packet
        cs = {device.read_msg(addr, msg) for device in self.devices.values()}
        if cs:
            await asyncio.wait(cs)
        if re.match('\s*desc\s+\w+\s+\w+\s*', msg):
            async with self.devices_changed:
                if addr not in {device.addr for device in self.devices.values()}:
                    com_debug(f'Network: No device with addr {addr}')
                    device = Device(addr=addr)
                    await device.read_msg(addr, msg)
                    self.add_device(device)
                    self.devices_changed.notify_all()

    async def _device_listening(self, device):
        while device in self.devices.values(): 
            async with device.desc_changed:
                await device.desc_changed.wait()
                com_debug(f'Network: Device {device} changed its desc')
                async with self.devices_changed:
                    self.devices_changed.notify_all()

    def add_bus(self, bus):
        uid = hex(id(bus))
        self.buses[uid] = bus
        self.create_task(self._device_radar(bus))
        self.create_task(self._bus_listening(bus))
        com_debug('Network: Bus added')
        return uid

    def add_device(self, device):
        uid = hex(id(device))
        self.devices[uid] = device
        self.create_task(self._device_listening(device))
        com_debug('Network: Device added')
        return uid

class Device(Node):

    def __init__(self, *, name=None, addr=None): 
        super().__init__()
        if name is None and addr is None: 
            raise RuntimeError()
        self.name = name
        self.addr = addr
        self.n_attr = None
        self.desc_changed = self.Condition()
        self.msg = None
        self.msg_changed = self.Condition()
        self.attrs = dict()
        self.attrs_changed = self.Condition()
        self.create_task(self._desc_fetching())
        self.create_task(self._attrs_fetching())
        com_debug(f'Device: Created')
        print(f'Device create {self.name} {self.addr}')

    async def _desc_fetching(self):
        while True:
            if self.name is None or self.n_attr is None:
                com_debug(f'Device: Incomplete desc') 
                try:
                    await self.send(f'get desc')
                except RuntimeError:
                    async with self.desc_changed:
                        await self.desc_changed.wait() # wait for reconnection
                else:
                    await asyncio.sleep(5)
            else:
                async with self.desc_changed:
                    await self.desc_changed.wait()

    async def _attrs_fetching(self):
        while True:
            com_debug('Device: Fetching attrs') 
            if self.n_attr is None:
                async with self.desc_changed:
                    await self.desc_changed.wait()
            else:
                #TODO too many
                if len(self.attrs) < self.n_attr:
                    attrs_ids = set(range(self.n_attr)) - self.attrs_ids
                    tasks = {self.create_task(self.send(f'get attr {attr_id}')) for attr_id in attrs_ids}
                    try:
                        done, pending = await asyncio.wait(tasks, return_when=asyncio.ALL_COMPLETED) 
                    except Exception as e:
                        print(e)
                        async with self.desc_changed:
                            await self.desc_changed.wait()
                    else:
                        await asyncio.sleep(5)
                else:
                    async with self.desc_changed:
                        await self.desc_changed.wait()

    async def read_msg(self, addr, msg):
        com_debug(f'Device: Read msg: {msg}') 
        if (
                self.disconnected and self.name is not None and
                re.match(f'\s*desc\s+{self.name}\s+\d+\s*', msg)
            ):
            self.addr = addr
        elif addr != self.addr:
            return
        async with self.msg_changed:
            self.msg = msg
            self.msg_changed.notify_all()
        cs = {attr.read_msg(msg) for attr in self.attrs.values()}
        if cs:
            await asyncio.wait(cs)
        if re.match('\s*desc\s+\w*\s+\d+\s*', msg):
            async with self.desc_changed:
                com_debug('Device: Set desc from msg')
                words = msg.split()
                name, n_attr = words[1], int(words[2]) 
                if self.name != name or self.n_attr != n_attr:
                    self.desc_changed.notify_all()
                self.name = name 
                self.n_attr = n_attr 
        elif re.match('\s*attr\s+\d+\s+\w+\s+\w+\s*', msg):
            attr_id = int(msg.split()[1])
            if attr_id not in self.attrs_ids:
                com_debug(f'Device: Attr {attr_id} not existant')
                attr = Attribute(self, attr_id=attr_id)
                await attr.read_msg(msg)
                self.add_attr(attr)

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
        com_debug(f'Device: Attr added')

    async def send(self, msg):
        bus = self.addr[0]
        device_id = self.addr[1]
        await bus.send(device_id, msg)

    @property
    def attrs_ids(self):
        return {a.attr_id for a in self.attrs.values() if a.attr_id is not None}

    @property
    def disconnected(self):
        if self.addr is None: #TODO or timed out
            return True
        return False

class Attribute(Node):

    def __init__(self, device,*, name=None, attr_id=None):
        super().__init__()
        self.device = device
        self.name = name
        self.attr_id = attr_id
        self.vtype = None 
        self._value = None 
        self.desc_changed = self.Condition()
        self.create_task(self._desc_fetching())
        self.create_task(self._value_fetching())
        com_debug('Attribute: Created')

    async def _desc_fetching(self):
        while True:
            if (self.name is None or self.vtype is None) and self.attr_id is not None:
                com_debug(f'Attribute: Incomplete desc') 
                try:
                    await self.device.send(f'get attr {self.attr_id}')
                except RuntimeError:
                    async with self.desc_changed:
                        await self.desc_changed.wait() # wait for reconnection
                else:
                    await asyncio.sleep(10)
            else:
                async with self.desc_changed:
                    await self.desc_changed.wait()

    async def _value_fetching(self):
        while True:
            if self._value is None and self.attr_id is not None: 
                com_debug(f'Attribute: No value') 
                try:
                    await self.device.send(f'get val {self.attr_id}')
                except RuntimeError:
                    async with self.desc_changed:
                        await self.desc_changed.wait() # wait for reconnection
                else:
                    await asyncio.sleep(10)
            else:
                async with self.desc_changed:
                    await self.desc_changed.wait()

    async def read_msg(self, msg):
        com_debug(f'Attribute: Read msg: {msg}')
        words = msg.split()
        if (
                self.attr_id is None and self.name is not None and
                re.match(f'\s*attr\s+\d+\s+{self.name}\s+\w+\s*', msg)
            ):
            async with self.desc_changed:
                self.attr_id = int(words[1])
                self.desc_changed.notify_all()
        elif self.attr_id is None:
            return
        if re.match(f'\s*attr\s+{self.attr_id}\s+\w+\s+\w+\s*', msg):
            async with self.desc_changed:
                name = words[2]
                vtype = words[3]
                if name != self.name or vtype != self.vtype:
                    self.desc_changed.notify_all()
                self.name = name
                self.vtype = vtype
        elif re.match(f'\s*val\s+{self.attr_id}\s+\w+\s*', msg):
            async with self.desc_changed:
                value = words[2]
                if value != self._value:
                    self.desc_changed.notify_all()
                self._value = value

    @property
    def value(self):
        if self._value is None:
            return None
        if self.vtype == 'int':
            return int(self._value)
        if self.vtype == 'bool':
            return bool(float(self._value))
        return self._value

