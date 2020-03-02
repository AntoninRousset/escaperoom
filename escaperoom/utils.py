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

def ensure_iter(obj, *, exceptions=[str]):
    for exception in exceptions:
        if isinstance(obj, exception):
            return obj
    if hasattr(obj, '__iter__'):
        return obj
    else:
        return (obj,)

async def dummy_coroutine():
    pass
