#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
from .config import get_config
from .data import get_data
from .cache import get_cache

_logger = logging.getLogger('escaperoom.storage')

# config
config = get_config()
_logger.debug('Config accessor loaded')

# data
_use_database = config['database'].getboolean('use_database')
_backend = config['database']['backend']
data = get_data(load_db=_use_database, db_backend=_backend)
_logger.debug('Data accessor loaded')

# cache
cache = get_cache()
_logger.debug('Cache accessor loaded')
