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

from ..logic import Puzzle
from ..misc import Camera
from ..network import Device

#TODO use the locks for reading? to ensure there is corruption 

def datetime_to_string(datetime):
    if datetime is not None:
        return datetime.strftime('%H:%M')

async def read(game, service, query=None):
    if service == 'cameras':
        return await cameras_reader(game)
    if service == 'chronometer':
        return await chronometer_reader(game)
    if service == 'device':
        return await device_reader(game, query)
    if service == 'devices':
        return await devices_reader(game)
    if service == 'game':
        return await game_reader(game)
    if service == 'puzzle':
        return await puzzle_reader(game, query)
    if service == 'puzzles':
        return await puzzles_reader(game)
    raise KeyError(service)

async def cameras_reader(game):
    cameras = {
            camera.id : {
                'name' : camera.name
                } for camera in Camera.nodes()
            }
    return {'cameras' : cameras}

async def chronometer_reader(game):
    running = game.start_time is not None and game.end_time is None
    return {
            'running' : running,
            'time' : game.chronometer.total_seconds()*1000
            }

async def device_reader(game, query):
    device = Device.find_node(**query)
    attrs = {
            id : {
                'attr_id' : attr.attr_id, 'name' : attr.name,
                'type' : attr.type,
                'value' : attr.value
                } for id, attr in device.attrs.items()
            }
    return {
            'id' : device.id,
            'name' : device.name,
            'attrs' : attrs,
            'type' : device.type,
            'addr' : None if device.disconnected() else device.addr[1],
            'msg' : device.msg,
            'state' : 'offline' if device.disconnected() else 'online'
            }

async def devices_reader(game):
    devices = {
            device.id : {
                'name' : device.name,
                'type' : device.type,
                'n_attr' : device.n_attr
                } for device in Device.nodes()
            }
    return {'devices' : devices}

async def game_reader(game):
    async with game.desc_changed:
        return {
                'running' : game.running,
                'name' : game.name,
                'start_time' : datetime_to_string(game.start_time),
                'end_time' : datetime_to_string(game.end_time),
                'default_options' : game.default_options
                }

async def puzzle_reader(game, query):
    puzzle = Puzzle.find_node(**query)
    async with puzzle.desc_changed:
        return {
                'id' : puzzle.id,
                'name' : puzzle.name,
                'state' : puzzle.state,
                'description' : puzzle.description
                }

async def puzzles_reader(game):
    puzzles = {
            puzzle.id : {
                'name' : puzzle.name,
                'state' : puzzle.state,
                'col' : puzzle.pos[0],
                'row' : puzzle.pos[1]
                } for puzzle in Puzzle.nodes()
            }
    return {'puzzles' : puzzles}

