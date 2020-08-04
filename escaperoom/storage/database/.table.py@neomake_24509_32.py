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

import sqlalchemy as sql
from weakref import ref


class DataTable(sql.Table):
    """
    Accessor for a table.
    """

    def __new__(cls, name, db, row_type, *args, **kwargs):
        """
        Parameters
        ----------
        name : str
            The name of the table in the database.
        db : Database
            Link the database.
        row_type : sub-type of DataRow
            The corresponding accessor for each row.
        *arg : any
            passed to the sql Table constructor.
        **kwarg : any -> any
            passed to the sql Table constructor.
        """

        tab = sql.Table.__new__(cls, name, db.metadata, *args, **kwargs)
        tab._db = ref(db)
        tab.row_type = row_type
        return tab

    @property
    def db(self):
        return self._db()

    def __getitem__(self, k):
        """
        Return the data row given by the key k.

        Parameters
        ----------
        key : any sql compatible type, list or dict
            The row key value for selection. For composite key, the key must be
            a list correctly ordered or a dict with the values for each primary
            key column.
        """

        return self.row_type(k, self)

    async def new(self, **kwargs):
        """
        Insert a new row the table.

        Parameters
        ----------
        **kwargs : str -> any sql compatible type
            Every kwargs value are inserted in the newly created row. The keys
            represent the columns names.

        Return
        ------
        row : DataRow sub-types
            Corresponding row accessor.
        """

        from sqlalchemy import select, text

        rowid = await self.db.execute(self.insert(), values=kwargs)
        query = select(self.primary_key).where(text(f'rowid == {rowid}'))
        key = await self.db.fetch_one(query)
        return self.row_type(key, self)

    async def __aiter__(self):
        select = sql.select(self.primary_key)
        # all rows are retrieved to avoid double connection (would fresh)
        keys = await self.db.fetch_all(select)
        for (key,) in keys:
            yield self.row_type(key, self)


class DataRow:
    """
    Accessor for a singe table row.
    """

    def __init__(self, key, table=None):
        """
        Parameters
        ----------
        key: any sql compatible type, dict, non-dict iterable or DataRow.
            The row key value for selection. For composite key, the key must be
            a list correctly ordered or a dict with the values for each primary
            key column. If an instance of DataRow is given, the latter is
            copied and table can be omitted.
        table: Table
            Table to read into. Can be ommited if key is an insance of DataRow.
        """

        if isinstance(key, DataRow):
            self.key = key.key
            self.tabel = key.table
            return

        if table is None:
            raise ValueError('Table cannot be ommited if key is not a '
                             'instance of DataRow')

        self.table = table

        if isinstance(key, dict):
            key = [key[c.name] for c in self.table.primary_key]

        if isinstance(key, str):
            key = [key]

        try:
            key = tuple(key)
        except TypeError:
            key = (key,)

        if len(key) != len(self.table.primary_key):
            raise ValueError('Key length does not match')

        self.key = key

    async def exists(self):
        """
        Return True if the row actually exists in the refered table. False
        otherise.
        """
        select = sql.select(self.table.primary_key).where(self._condition)
        res = await self.db.fetch_one(select)
        return res is not None

    @property
    def db(self):
        return self.table.db

    async def get(self, c):
        """
        Return the value of the given column.

        Parameters
        ----------
        c: str
            Column name.
        """
        select = self.table.select().where(self._condition)
        return await self.db.fetch_val(select, column=self.table.c[c])

    async def get_many(self, columns):
        """
        Return the value of the given columns in the given order.

        Parameters
        ----------
        columns: iterable or dict
            Column names. The values of the iterable should be the column
            names. If a dict is given, it will be used as a map to rename the
            result key dict.

        Return
        ------
        columns: dict
            The column content. The keys is the name of the column or the given
            keys if columns is a dict and the values are the column content.
        """
        keys = columns.keys() if isinstance(columns, dict) else columns
        columns = columns.values() if isinstance(columns, dict) else columns
        columns = [self.table.c[c] for c in columns]
        select = sql.select(columns).where(self._condition)
        values = await self.db.fetch_one(select)
        return dict(zip(keys, values))

    @property
    def _condition(self):
        return sql.and_(*(k1 == k2 for k1, k2 in zip(self.table.primary_key,
                                                     self.key)))

    async def remove(self):
        """
        Remove the corresponding row in the table. Won't raise an exeption if
        the row doesn't actually exists.
        """
        await self.db.execute(self.table.delete().where(self._condition))

    def __repr__(self):
        return f'<{type(self).__name__} {self.key} in table {self.table.name}>'

    def __hash__(self):
        return hash((self.table, self.key))

    def __equ__(self, d):
        return (self.table, self.key) == (d.table, d.key)
