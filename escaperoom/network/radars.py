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

from . import asyncio, RemoteDevice

logger = logging.getLogger('escaperoom.network')

class SerialRadar():

    _group = dict()

    def __init__(self):
        super().__init__()
        self.packet = None
        self.packet_changed = asyncio.Condition()
        self.buses = dict()
        self.buses_changed = asyncio.Condition()
        self.devices = dict()
        self.devices_changed = asyncio.Condition()

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
                        try:
                            await self.read_msg(addr, msg)
                        except Exception as e:
                            logger.error(f'{self}: error processing msg "{msg}": {e}')
                await bus.packet_changed.wait()

    def find_device(self, *, id=None, name=None, addr=None):
        if id is not None:
            return id, self.devices[id]
        for id, device in self.devices.items():
            if not device.disconnected() and device.addr[0] == addr[0]:
                if device.addr[1] == addr[1] or device.addr[1] == 0:
                    return id, device
            if device.name == name:
                return id, device
        return None, None

    async def read_msg(self, sender, msg): 
        logger.debug(f'{self}: reading msg "{msg}"') 
        if re.match('\s*desc\s+\w+\s+\w+\s*', msg):
            name = msg.split()[1]
            _, device = self.find_device(name=name, addr=sender)
            if device is None:
                logger.debug(f'{self}: no device with id 0x{sender[1]:02x}')
                device = RemoteDevice(addr=sender, name=name)
                async with self.devices_changed:
                    self.add_device(device)
                    self.devices_changed.notify_all()
            else:
                logger.debug(f'{self}: found device with id 0x{sender[1]:02x}')
                async with device.desc_changed:
                    if device.addr != sender or device.name != name:
                        device.desc_changed.notify_all()
                    device.addr, device.name = sender, name
        _, device = self.find_device(addr=sender)
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
        _id = hex(id(bus))
        self.buses[_id] = bus
        asyncio.create_task(self._device_radar(bus))
        asyncio.create_task(self._bus_listening(bus))
        logger.debug(f'{self}: {bus} added')

    def add_device(self, device):
        _id = hex(id(device))
        self.devices[_id] = device
        asyncio.create_task(self._device_listening(device))
        logger.debug(f'{self}: {device} added')

    def create_device(self, *args, **kwargs):
        device = RemoteDevice(*args, **kwargs)
        self.add_device(device)
        return device

