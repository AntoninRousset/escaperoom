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
 
async def game(_game):
    while True:
        async with _game.desc_changed:
            await _game.desc_changed.wait()
            yield {'type' : 'update', 'loc' : f'/{_game.name}/game'}

async def chronometer(game):
    while True:
        async with game.desc_changed:
            await game.desc_changed.wait()
            yield {'type' : 'update', 'loc' : f'/{game.name}/chronometer'}

async def puzzles(game):
    while True:
        async with game.logic.puzzles_changed:
            await game.logic.puzzles_changed.wait()
            yield {'type' : 'update', 'loc' : f'/{game.name}/puzzles'}

async def devices(game):
    while True:
        async with game.network.devices_changed:
            await game.network.devices_changed.wait()
            yield {'type' : 'update', 'loc' : f'/{game.name}/devices'}

event_generators = {game, chronometer, puzzles, devices}

