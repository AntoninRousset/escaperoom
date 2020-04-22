#!/usr/bin/env python
# -*- coding: utf-8 -*-

from json import dumps


def to_json(obj):
    """
    Serialize obj to a JSON formatted str.

    This function extends the serializable obj to any obj implementing a
    __json__ method. The latter function must take no arguments except self and
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
        try:
            return obj.__json__()
        except AttributeError:
            t = type(obj).__name__
            raise TypeError(f'Object of type \'{t}\' is not JSON serializable')

    return dumps(obj, default=default)
