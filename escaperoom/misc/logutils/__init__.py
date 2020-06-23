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

from logging import WARNING, DEBUG


def init_logging_system(log_file='/tmp/escaperoom.log', level='WARNING'):

    from logging import getLogger, getLevelName

    invalid_level = level
    if isinstance(level, str):
        level = getLevelName(level)

    # if getLevelName failed to get level number, a string is returned
    if isinstance(level, str):
        level = WARNING
    else:
        invalid_level = False

    logger = getLogger()
    logger.setLevel(DEBUG)
    add_stderr_handler(logger, level=level)
    add_file_handler(logger, log_file, level=DEBUG)

    if invalid_level:
        logger.error(f'Invalid logging level {invalid_level}, fallback to '
                     'WARNING (the default).')

    logger.debug(f'Debug system initialized with log_file: {log_file} and '
                 f'level: {level}')


def add_stderr_handler(logger, level=WARNING):

    from .formatter import ColoredFormatter as Formatter
    from logging import StreamHandler

    handler = StreamHandler()
    handler.setLevel(level)

    form = Formatter('%(levelcolor)s%(levelname_pad)s%(resetcolor)s '
                     '%(message)s')
    handler.setFormatter(form)
    logger.addHandler(handler)


def add_file_handler(logger, log_file, level=DEBUG):

    from .formatter import ColoredFormatter as Formatter
    from logging import FileHandler

    handler = FileHandler(str(log_file))
    handler.setLevel(level)

    form = Formatter('%(levelcolor)s%(asctime)s - %(name)s - %(levelname)s '
                     '%(resetcolor)s\n'
                     '  %(legendcolor)sProcess: %(processName)s '
                     '  Thread: %(threadName)s %(resetcolor)s\n'
                     '  %(legendcolor)s%(location)s: %(resetcolor)s\n'
                     '  %(message)s\n')
    handler.setFormatter(form)
    logger.addHandler(handler)
