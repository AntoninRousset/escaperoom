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

import logging
from .config import get_config
from .data import get_data
from .cache import get_cache

_logger = logging.getLogger('escaperoom.storage')

# config
config = get_config()
_logger.debug('Config accessor loaded')

# data
data = get_data(load_db=config.use_database,
                db_backend=config.database_backend)
_logger.debug('Data accessor loaded')

# cache
cache = get_cache()
_logger.debug('Cache accessor loaded')
