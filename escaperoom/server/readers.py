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
from ..logic import Action, Condition
from ..misc import Camera, Chronometer
from ..network import Device


async def read(service, query=None, server=None):
    if service == 'actions':
        return await actions_reader()
    if service == 'action':
        return await action_reader(query)
    if service == 'cameras':
        return await cameras_reader()
    if service == 'chronometer':
        return await chronometer_reader(query, server)
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
    if service == 'gamemasters':
        return await gamemasters_reader()
    raise KeyError(service)

#TODO a reader should take a set of entries, like actions so it can be reused
async def actions_reader():
    actions = {
            action.id : {
                'name' : action.name,
                'desactivated' : action.desactivated,
                'desc' : action.name if action.desc is None else action.desc,
                'running' : action.running,
                'failed' : action.failed
                } for action in Action.entries()
            }
    return {'actions' : actions}

async def action_reader(query):
    action = Action.find_entry(**query)
    return {
            'id' : action.id,
            'name' : action.name,
            'desactivated' : action.desactivated,
            'desc' : action.name if action.desc is None else action.desc,
            'running' : action.running,
            'failed' : action.failed
            }

async def cameras_reader():
    cameras = {
            camera.id : {
                'name' : camera.name
                } for camera in Camera.entries()
            }
    return {'cameras' : cameras}

async def chronometer_reader(query, server=None):
    if 'name' in query or 'id' in query:
        chronometer = Chronometer.find_entry(query.get('name'),
                                             id=query.get('id'))
    elif server is not None:
        chronometer = server.main_chronometer
    if chronometer is None: return ''
    return {
            'speed' : chronometer.speed,
            'time' : chronometer.time.total_seconds()*1000
            }

async def conditions_reader():
    conditions = {
            condition.id : {
                'name' : condition.name,
                'state' : condition.state,
                'forced': condition.forced,
                'row' : None if condition.pos is None else condition.pos[0],
                'col' : None if condition.pos is None else condition.pos[1],
                } for condition in Condition.entries()
            }
    return {'conditions' : conditions}

async def condition_reader(query):
    condition = Condition.find_entry(**query)
    actions = {
            action.id : {
                'name' : action.name,
                'desc' : action.name if action.desc is None else action.desc,
                'desactivated' : action.desactivated,
                'running' : action.running,
                'failed' : action.failed
                } for action in condition.actions
            }

    c_siblings = condition.siblings
    if c_siblings is None:
        c_siblings = {s for s in condition._listens | condition._parents if
                      isinstance(s, Condition)}
    siblings = {
            sibling.id : {
                'name' : sibling.name,
                'desc' : sibling.name if sibling.desc is None else sibling.desc,
                'state' : bool(sibling),
                'desactivated' : sibling.desactivated,
                } for sibling in c_siblings
            }
    return {
            'id' : condition.id,
            'name' : condition.name,
            'desc' : condition.name if condition.desc is None else condition.desc,
            'msg' : condition.msg,
            'state' : bool(condition),
            'desactivated' : condition.desactivated,
            'forced': condition.forced,
            'description' : condition.desc,
            'siblings' : siblings,
            'actions' : actions,
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
            'desc' : device.name if device.desc is None else device.desc,
            'attrs' : attrs,
            'type' : device.type,
            }


async def devices_reader():
    devices = {
            device.id: {
                'name': device.name,
                'desc': device.name if device.desc is None else device.desc,
                'type': '?' if device.type == 'unknown' else device.type,
                'n_attr': device.n_attr
                } for device in Device.entries()
            }
    return {'devices': devices}


async def game_reader():
    return Game.get()


async def gamemasters_reader():
    from .. import storage
    return await storage.data.db.gamemasters.get_all()
