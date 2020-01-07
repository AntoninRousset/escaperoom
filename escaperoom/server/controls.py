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

async def game(game, params):
    if params['action'] == 'new_game':
        options = params['options']
        await game.new_game(options)
    elif params['action'] == 'stop_game':
        await game.stop_game()
    elif params['action'] == 'force_activation':
        uid = params['uid']
    return ''
