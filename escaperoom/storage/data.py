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


def get_data(platform=None, load_db=False, db_backend='sqlite'):
    """
    Get a data accessor suitable for the given platform.

    Parameters
    ----------
    platform : str
        System platform name. If not set, automatically retrieved from the
        in-use platform.
    load_db : bool
        If True, load the database.
    db_backend : str
        Database backend. Ignored if load_db is False.

    Returns
    -------
    data : subclass of DataAccessor
        A data accessor.
    """

    if platform is None:
        import sys
        platform = sys.platform

    if platform == 'linux':
        return XDGDataAccessor(load_db, db_backend)
    else:
        raise SystemError(f'Unsupported system platform {sys.platform}')


class DatabaseNotLoadedException(Exception):
    pass


class DataAccessor:

    def __init__(self, dirpath, load_db=False, db_backend='sqlite'):

        from pathlib import Path

        self.dirpath = Path(dirpath)
        self.dirpath.mkdir(parents=True, exist_ok=True)
        self._db = None

        if load_db:
            self._db = self.load_db(db_backend)

    @property
    def is_db_loaded(self):
        return self._db is not None

    @property
    def db(self):
        if not self.is_db_loaded:
            raise DatabaseNotLoadedException('Make sure that use_database '
                                             'config is not set to False')

        return self._db

    def load_db(self, backend='sqlite'):

        from .database import Database

        filename = str(self.dirpath / 'escaperoom.db')
        return Database(f'/{filename}', backend)


class XDGDataAccessor(DataAccessor):

    dirname = 'escaperoom'

    def __init__(self, load_db=False, db_backend='sqlite'):

        from xdg.BaseDirectory import xdg_data_home
        from pathlib import Path
        dirpath = Path(xdg_data_home) / self.dirname

        super().__init__(dirpath, load_db, db_backend)
