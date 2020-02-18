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

from ..game import Game
from ..logic import Condition
from ..misc import Camera, Chronometer
from ..network import Device


def datetime_to_string(datetime):
    if datetime is not None:
        return datetime.strftime('%H:%M')

async def read(service, query=None):
    if service == 'cameras':
        return await cameras_reader()
    if service == 'chronometer':
        return await chronometer_reader()
    if service == 'device':
        return await device_reader(query)
    if service == 'devices':
        return await devices_reader()
    if service == 'game':
        return await game_reader()
    if service == 'condition':
        return await condition_reader(query)
    if service == 'conditions':
        return await conditions_reader()
    raise KeyError(service)

async def cameras_reader():
    cameras = {
            camera.id : {
                'name' : camera.name
                } for camera in Camera.entries()
            }
    return {'cameras' : cameras}

async def chronometer_reader():
    chronometer = Chronometer.find_entry('__game')
    if chronometer is None: return ''
    return {
            'running' : chronometer.is_running(),
            'time' : chronometer.elapsed().total_seconds()*1000
            }

async def device_reader(query):
    device = Device.find_entry(**query)
    attrs = None if device._attrs is None else dict()
    if device._attrs is None:
        attrs = None
    else:
        attrs = {
                attr_id : {
                    'attr_id' : attr_id,
                    'name' : attr.name,
                    'type' : attr.type,
                    'value' : attr.value
                    } for attr_id, attr in zip(range(device.n_attr), device._attrs)
                }
    return {
            'id' : device.id,
            'name' : device.name,
            'attrs' : attrs,
            'type' : device.type,
            }

async def devices_reader():
    devices = {
            device.id : {
                'name' : device.name,
                'type' : device.type,
                'n_attr' : device.n_attr
                } for device in Device.entries()
            }
    return {'devices' : devices}

async def game_reader():
    return {
            'running' : Game.is_running(),
            'name' : Game.name,
            'start_time' : datetime_to_string(Game._chronometer.start_time),
            'end_time' : datetime_to_string(Game._chronometer.end_time),
            'default_options' : Game.default_options
            }

async def condition_reader(query):
    condition = condition.find_entry(**query)
    return {
            'id' : condition.id,
            'name' : condition.name,
            'state' : condition.state,
            'description' : condition.desc
            }

async def conditions_reader():
    conditions = {
            condition.id : {
                'name' : condition.name,
                'state' : 'done' if condition else 'active' if condition.active else 'inactive',
                'row' : None if condition.pos is None else condition.pos[0],
                'col' : None if condition.pos is None else condition.pos[1],
                } for condition in Condition.entries()
            }
    return {'conditions' : conditions}

