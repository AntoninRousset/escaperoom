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

from configparser import ConfigParser


def get_config(platform=None):
    """
    Get a config accessor suitable for the given platform.

    Parameters
    ----------
    platform : str
        System platform name. If not set, automatically retrieved from the
        in-use platform.

    Returns
    -------
    config: subclass of ConfigAccessor
        A config accessor.
    """

    if platform is None:
        import sys
        platform = sys.platform

    if platform == 'linux':
        return XDGConfigAccessor()
    else:
        raise SystemError(f'Unsupported system platform {sys.platform}')


class ConfigAccessor:

    dirname = 'escaperoom'


class XDGConfigAccessor(ConfigAccessor):

    def __init__(self, filename=None):

        super().__init__()

        self.general = self.load_config_file('general.conf')
        self.logging = self.load_config_file('logger.conf')
        self.rooms = self.load_config_file('rooms.conf')

    def load_config_file(self, name):

        from pathlib import Path

        default_config_file = Path(__file__).absolute().parent / name
        user_config_file = self.config_dir / name

        config = ConfigParser()
        config.read([default_config_file, user_config_file], encoding='utf-8')
        return config

    @property
    def rooms_dir(self):
        return self.general['DEFAULT']['rooms_dir']

    @property
    def test(self):
        return self.general['DEFAULT'].getboolean('test')

    @property
    def use_database(self):
        return self.general['database'].getboolean('use_database')

    @property
    def database_backend(self):
        return self.general['database']['backend']

    @property
    def config_dir(self):

        from xdg.BaseDirectory import xdg_config_home
        from pathlib import Path

        return Path(xdg_config_home) / self.dirname
