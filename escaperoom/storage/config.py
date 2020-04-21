#!/usr/bin/env python
# -*- coding: utf-8 -*-

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


class ConfigAccessor(ConfigParser):

    dirname = 'escaperoom'


class XDGConfigAccessor(ConfigAccessor):

    def __init__(self, filename=None):

        super().__init__()

        from pathlib import Path

        default_file = Path(__file__).absolute().parent / 'default.conf'
        filename = filename or self._get_default_filename()
        config_file = Path(filename).expanduser()
        self.read([default_file, config_file], encoding='utf-8')

    def use_(self):

        """
        Get the database if the "use_database" is True in the config.

        Returns
        -------
        database : Databse or None
            A Database object if "use_database" is True. None otherwise.
        """

        if not self['database'].getboolean('use_database'):
            return None

        from .data import data

        return data.load_database(backend=self['database']['backend'])

    def _get_default_filename(self):

        from xdg.BaseDirectory import xdg_config_home
        from pathlib import Path

        return Path(xdg_config_home) / self.dirname / 'escaperoom.conf'
