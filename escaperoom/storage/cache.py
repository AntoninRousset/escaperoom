#!/usr/bin/env python
# -*- coding: utf-8 -*-

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
