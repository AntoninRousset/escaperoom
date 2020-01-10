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

async def control(game, params, service, query=None):
    if service == 'camera':
        return await camera_control(game, params, query)
    if service == 'display':
        return await display_control(game, params)
    if service == 'game':
        return await game_control(game, params)
    if service == 'puzzle':
        return await puzzle_control(game, params, query)

async def camera_control(game, params, query):
    _, camera = game.misc.find_camera(**query)
    return await camera.handle_sdp(params['sdp'], params['type'])

async def display_control(game, params):
    display = game.misc.display
    return await display.set_msg(params['msg'])

async def game_control(game, params):
    if params['action'] == 'new_game':
        options = params['options']
        await game.new_game(options)
    elif params['action'] == 'stop_game':
        await game.stop_game()
    return ''

async def puzzle_control(game, params, query):
    _, puzzle = game.logic.find_puzzle(**query)
    if params['action'] == 'activate':
        async with puzzle.desc_changed:
            puzzle.force_active = True
            puzzle.desc_changed.notify_all()
    elif params['action'] == 'complete':
        async with puzzle.desc_changed:
            puzzle.force_completed = True
            puzzle.desc_changed.notify_all()
    elif params['action'] == 'restore':
        async with puzzle.desc_changed:
            puzzle.force_active = False
            puzzle.force_completed = False
            puzzle.desc_changed.notify_all()

