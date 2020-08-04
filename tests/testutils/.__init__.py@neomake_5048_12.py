#!/usr/bin/env python
# -*- coding: utf-8 -*-


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


class TestError(Exception):
    pass


def run(func_or_coro, name=None):

    import asyncio

    name = name or ''

    failed = ANSI['reset'] + ANSI['red'] + ANSI['bold'] + 'FAILED' \
        + ANSI['reset']
    success = ANSI['reset'] + ANSI['green'] + ANSI['bold'] + 'SUCCESS' \
        + ANSI['reset']

    print(f'{ANSI["reset"]}{ANSI["bold"]} * {ANSI["reset"]}'
          f'{name}... ', end='')

    try:
        if asyncio.iscoroutine(func_or_coro):
            loop = asyncio.get_event_loop()
            res = loop.run_until_complete(func_or_coro)
        else:
            res = func_or_coro()

        if isinstance(res, str):
            print(failed)
            print('->', res)
        else:
            print(success)

    except BaseException as e:
        from traceback import print_stack
        print(failed)
        print_stack()


def random_hex():
    from random import randint
    key = randint(1, 1 << 64) - 1
    return f'{key:016x}'


def random_key():
    return 'test/' + random_hex()


def random_string(nmin=4, nmax=32):
    from random import randint, choices
    from string import printable
    return choices(printable, k=randint(nmin, nmax))

def random_int():
    from random import randint
    return randint(1, 1 << 64) - 1
