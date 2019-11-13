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

async def devices(game):
    while True:
        async with game.network.devices_changed:
            descs = dict()
            for uid, device in game.network.devices.items():
                descs[uid] = {'name' : device.name, 'n_attr' : device.n_attr}
            yield descs
            await game.network.devices_changed.wait()

async def device(game, uid):
    device = game.network.devices[uid]
    while True:
        attrs = {uid : {'name' : attr.name, 'type' : attr.vtype, 'value' : attr.value}
                for uid, attr in device.attrs.items()}
        info = {'name' : device.name, 'attrs' : attrs,
                'addr' : device.addr, 'msg' : device.msg}
        yield info
        await device.changed.wait()

async def puzzles(game):
    while True:
        async with game.logic.puzzles_changed:
            descs = dict()
            for uid, puzzle in game.logic.puzzles.items():
                col, row = game.logic.positions[uid]
                descs[uid] = {'name' : puzzle.name, 'state' : puzzle.state,
                              'row' : row, 'col' : col} 
            yield descs
            await game.logic.puzzles_changed.wait()

async def puzzle(game, uid):
    puzzle = game.logic.puzzles[uid]
    while True:
        info = {'uid' : uid, 'name' : puzzle.name}
        yield info
        await puzzle.changed.wait()

def cameras(game):
    descs = dict()
    for uid, camera in game.misc.cameras.items():
        descs[uid] = {'name' : camera.name}
    descs_changed = game.misc.cameras_changed
    return descs, descs_changed

