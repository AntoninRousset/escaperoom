import logging
from pathlib import Path
from tempfile import mkstemp
import os
from shutil import move
import json
from itertools import groupby

logger = logging.getLogger('escaperoom.misc.history')


class History:

    def __init__(self, filepath, max_length=1000, any_extension=False):
        self.filepath = self._check_filepath(filepath, any_extension)
        self.max_length = max_length
        self.data = self._load_file(self.filepath)

    def push(self, line):
        self.data = (self.data + [line])[-self.max_length:]

    def most_frequents(self, n=20):
        fq = [(len(list(g)), k) for k, g in groupby(sorted(self.data))]
        return [k for n, k in sorted(fq, key=lambda x: x[0], reverse=True)]

    def __iter__(self):
        return iter(self.data)

    def __len__(self):
        return len(self.data)

    def __getitem__(self, k):
        return self.data[k]

    def _check_filepath(self, fp, any_extension):
        fp = Path(fp)
        if not any_extension and fp.suffix != '.hist':
            logger.error(f'Invalid history file extension: {fp}')
            return None
        return fp

    def _load_file(self, fp):

        if not fp:
            return None

        # try to touch history file
        try:
            self.filepath.touch()
        except BaseException:
            logger.exception(f'Failed to touch: {fp}')
            return []

        # try to load data
        try:
            with open(fp, 'r') as f:
                return json.load(f)[-self.max_length:]
        except BaseException:
            logger.exception(f'Failed to load: {fp}')
            return []

    def _save_file(self, fp):

        # try to write to a temporary file
        try:
            tmp_fd, tmp_fp = mkstemp()
            with open(tmp_fp, 'w') as f:
                json.dump(self.data[-self.max_length:], f, indent=0)
        except BaseException:
            logger.exception(f'Failed to write tmp file: {tmp_fp}')

        # try to move temporary file to history file
        try:
            move(tmp_fp, fp)
            os.close(tmp_fd)
        except BaseException:
            logger.exception(f'Failed to save history file: {fp}')

    def __del__(self):
        self._save_file(self.filepath)
