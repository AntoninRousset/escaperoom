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

def datetime_to_string(datetime):
    if datetime is not None:
        return datetime.strftime('%H:%M')

#Not used
def parse_timedelta(timedelta):
    if timedelta is not None:
        days = timedelta.days
        hours, remaining = divmod(timedelta.seconds, 3600)
        minutes, seconds = divmod(remaining, 60)
        return days, hours, minutes, seconds

async def game(game):
    async with game.desc_changed:
        return {'running' : game.running,
                'name' : game.name,
                'start_time' : datetime_to_string(game.start_time),
                'end_time' : datetime_to_string(game.end_time),
                'default_options' : game.default_options}

async def chronometer(game):
    running = game.start_time is not None and game.end_time is None
    return {'running' : running, 'time' : game.chronometer.total_seconds()*1000}

async def devices(game):
    async with game.network.devices_changed:
        devices = dict()
        for uid, device in game.network.devices.items():
            devices[uid] = {'name' : device.name,
                            'type' : device.type,
                            'n_attr' : device.n_attr}
        return {'devices' : devices}

async def device(game, uid):
    device = game.network.devices[uid]
    attrs = {uid : {'attr_id' : attr.attr_id, 'name' : attr.name, 'type' : attr.type_str(),
             'value' : attr.value} for uid, attr in device.attrs.items()}
    return {'name' : device.name,
            'attrs' : attrs,
            'type' : device.type,
            'addr' : None if device.disconnected() else device.addr[1],
            'msg' : device.msg,
            'state' : 'offline' if device.disconnected() else 'online'}

async def puzzles(game):
    async with game.logic.puzzles_changed:
        puzzles = dict()
        for uid, puzzle in game.logic.puzzles.items():
            col, row = game.logic.positions[uid]
            puzzles[uid] = {'name' : puzzle.name, 'state' : puzzle.state,
                          'row' : row, 'col' : col} 
        return {'puzzles' : puzzles}

async def puzzle(game, uid):
    puzzle = game.logic.puzzles[uid]
    return {'uid' : uid,
            'name' : puzzle.name,
            'state' : puzzle.state,
            'description' : puzzle.description}

async def cameras(game):
    async with game.misc.cameras_changed: 
        cameras = dict()
        for uid, camera in game.misc.cameras.items():
            cameras[uid] = {'name' : camera.name}
        return {'cameras' : cameras}

