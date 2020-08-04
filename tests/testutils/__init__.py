from . import random
from .colors import ANSI


class TestError(Exception):
    pass


def run(func_or_coro, name=None):

    import asyncio

    name = name or ''

    failed = ANSI['reset'] + ANSI['red'] + ANSI['bold'] + 'FAILED' \
        + ANSI['reset']
    interrupted = ANSI['reset'] + ANSI['blue'] + ANSI['bold'] + 'INTERRUPTED' \
        + ANSI['reset']
    success = ANSI['reset'] + ANSI['green'] + ANSI['bold'] + 'SUCCESS' \
        + ANSI['reset']

    print(f'{ANSI["reset"]}{ANSI["bold"]} * {ANSI["reset"]}'
          f'{name}... ', end='', flush=True)

    try:
        if asyncio.iscoroutine(func_or_coro):
            loop = asyncio.get_event_loop()
            loop.run_until_complete(func_or_coro)
        else:
            func_or_coro()
        print(success)

    except KeyboardInterrupt:
        print(interrupted)

    except BaseException as e:
        from traceback import print_exc
        print(failed)
        print_exc()

    print('-' * 80)
