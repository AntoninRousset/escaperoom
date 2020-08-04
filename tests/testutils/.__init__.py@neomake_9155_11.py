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


def print_start_test(name, func_or_coro):

    import asyncio

    print(f'Testing {name}...', end='')

    if asyncio.is_coroutine(func_or_coro):
        loop = asyncio.get_event_loop()

