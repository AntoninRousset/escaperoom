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

# TODO implement the cache accessor


def get_cache(platform=None):
    """
    Get a cache accessor suitable for the given platform.

    Parameters
    ----------
    platform : str
        System platform name. If not set, automatically retrieved from the
        in-use platform.

    Returns
    -------
    cache : subclass of CacheAccessor
        A cache accessor.
    """

    if platform is None:
        import sys
        platform = sys.platform

    if platform == 'linux':
        return XDGCacheAccessor()
    else:
        raise SystemError(f'Unsupported system platform {sys.platform}')


class CacheAccessor:

    dirname = 'escaperoom'

    def __init__(self):
        pass


class XDGCacheAccessor(CacheAccessor):

    def __init__(self, filename=None):
        super().__init__()
