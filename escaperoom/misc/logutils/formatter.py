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

from logging import Formatter
from collections import defaultdict

ANSI = {
    'reset': '\033[0m',
    'bold': '\033[1m',
    'italic': '\033[3m',
    'black': '\033[30m',
    'red': '\033[31m',
    'green': '\033[32m',
    'yellow': '\033[33m',
    'blue': '\033[34m',
    'magenta': '\033[35m',
    'cyan': '\033[36m',
    'white': '\033[37m',
    'bright_black': '\033[90m',
    'bright_red': '\033[91m',
    'bright_green': '\033[92m',
    'bright_yellow': '\033[93m',
    'bright_blue': '\033[94m',
    'bright_magenta': '\033[95m',
    'bright_cyan': '\033[96m',
    'bright_white': '\033[97m'
}


class ColoredFormatter(Formatter):

    levelcolors = {
        'ERROR': ANSI['bold'] + ANSI['bright_red'],
        'WARNING': ANSI['bold'] + ANSI['bright_yellow'],
        'INFO': ANSI['bold'] + ANSI['bright_black'],
        'DEBUG': ANSI['bold'] + ANSI['bright_blue']
    }

    def __init__(self, fmt=None, datefmt=None, style='%'):
        super().__init__(fmt=fmt, datefmt=datefmt, style=style)

    def format(self, record):

        # location is a relative path if the file is local (within the 
        # escaperoom) main directory and absolute if the logging call was
        # issued from an external module followed by the line number and the 
        # function name. If record.pathname is not available
        # location fallbacks to the string "???".
        import __main__
        from os.path import realpath, dirname

        try:
            main_dir = dirname(realpath(__main__.__file__))
            if record.pathname.startswith(main_dir):
                record.location = record.pathname.split(f'{main_dir}/')[-1]
            else:
                record.location = record.pathname
            record.location += f' line {record.lineno} in {record.funcName}'
        except BaseException:
            record.location = '???'

        record.resetcolor = ANSI['reset']
        record.levelcolor = self.levelcolors[record.levelname]
        record.levelname_pad = record.levelname.ljust(7)
        record.legendcolor = ANSI['italic'] + ANSI['bright_black']
        return super().format(record)
