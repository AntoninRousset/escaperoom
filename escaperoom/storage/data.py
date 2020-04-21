#!/usr/bin/env python
# -*- coding: utf-8 -*-


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


class DataAccessor:

    def __init__(self, dirpath, load_db=False, db_backend='sqlite'):

        from pathlib import Path

        self.dirpath = Path(dirpath)
        self.dirpath.mkdir(parents=True, exist_ok=True)
        self.db = None

        if load_db:
            self.load_db(db_backend)

    def load_db(self, backend='sqlite'):

        from .database import Database

        filename = str(self.dirpath / 'escaperoom.db')
        self.db = Database(f'/{filename}', backend)


class XDGDataAccessor(DataAccessor):

    dirname = 'escaperoom'

    def __init__(self, load_db=False, db_backend='sqlite'):

        from xdg.BaseDirectory import xdg_data_home
        from pathlib import Path
        dirpath = Path(xdg_data_home) / self.dirname

        super().__init__(dirpath, load_db, db_backend)
