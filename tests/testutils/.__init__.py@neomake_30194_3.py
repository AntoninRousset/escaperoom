from .colors import ANSI


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
