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

from ..misc import Camera, Display

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
    if service == 'displays':
        return await displays_reader(game)
    if service == 'game':
        return await game_reader(game)
    if service == 'puzzle':
        return await puzzle_reader(game, query)
    if service == 'puzzles':
        return await puzzles_reader(game)
    raise KeyError(service)

async def cameras_reader(game):
    cameras = {
            id : {
                'name' : camera.name
                } for id, camera in Camera.cameras.items()
            }
    return {'cameras' : cameras}

async def chronometer_reader(game):
    running = game.start_time is not None and game.end_time is None
    return {
            'running' : running,
            'time' : game.chronometer.total_seconds()*1000
            }

async def device_reader(game, query):
    id, device = game.network.find_device(**query)
    attrs = {
            id : {
                'attr_id' : attr.attr_id, 'name' : attr.name,
                'type' : attr.type,
                'value' : attr.value
                } for id, attr in device.attrs.items()
            }
    return {
            'id' : id,
            'name' : device.name,
            'attrs' : attrs,
            'type' : device.type,
            'addr' : None if device.disconnected() else device.addr[1],
            'msg' : device.msg,
            'state' : 'offline' if device.disconnected() else 'online'
            }

async def devices_reader(game):
    devices = {
            id : {
                'name' : device.name,
                'type' : device.type,
                'n_attr' : device.n_attr
                } for id, device in game.network.devices.items()
            }
    return {'devices' : devices}

async def displays_reader(game):
    displays = {
            uid : {
                'name' : display.name,
                } for uid, display in Display.displays.items()
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
    id, puzzle = game.logic.find_puzzle(**query)
    async with puzzle.desc_changed:
        return {
                'id' : id,
                'name' : puzzle.name,
                'state' : puzzle.state,
                'description' : puzzle.description
                }

async def puzzles_reader(game):
    puzzles = {
            id : {
                'name' : puzzle.name,
                'state' : puzzle.state,
                'col' : game.logic.positions[id][0],
                'row' : game.logic.positions[id][1]
                } for id, puzzle in game.logic.puzzles.items()
            }
    return {'puzzles' : puzzles}

