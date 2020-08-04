#!/usr/bin/env python
# -*- coding: utf-8 -*-

from json import dumps
from datetime import date, datetime, timedelta

# TODO add warning when converting dict with non-string (or just numerical)
# keys (type will be lost)


def to_json(obj):
    """
    Serialize obj to a JSON formatted str.

    This function extends the serializable obj types, adding:
        - datetime.datetime
        - any obj implementing __json__
    The __json__ method must not take any arguments except self and
    must return any json compatible obj: str, int, float, bool, None.

    Parameters
    ----------
    obj : str, int, float, bool, None or any object implementing __json__
        An object to serialization.

    Returns
    -------
    json : str
        The JSON formatted serialization of obj.
    """

    def default(obj):

        # datetime.datime is a subclass of datetime.daet
        if isinstance(obj, date):
            return obj.isoformat()

        if isinstance(obj, timedelta):
            return obj.total_seconds()

        if not hasattr(obj, '__json__'):
            raise TypeError(f'Object of type \'{type(obj)}\' is not JSON '
                            'serializable')

        return obj.__json__()

    return dumps(obj, default=default)