#!/usr/bin/env python
# -*- coding: utf-8 -*-

from pathlib import Path
from sys import path
path.insert(0, str(Path(__file__).absolute().parent.parent))


import testutils
from testutils import run, TestError
from escaperoom.shared.etcd import Etcd


async def perform_access_with_content(etcd, content, n=3):

    key = testutils.random.random_key()
    node = etcd.root / key

    for i in range(n):
        await node.set(content)
        if not await node.exists():
            raise TestError(f'Does not exist after set {i} to {content}')
        if await node.get() != content:
            raise TestError(f'Wrong data after set {i} to {content}')

        await node.delete()
        if await node.exists():
            raise TestError(f'Exists after delete {i}')
        try:
            await node.get()
            raise TestError(f'Get does not raise exception after delete {i}')

        except KeyError:
            pass


async def test_access(content_type, n=10):

    async with Etcd() as etcd:

        list_prefix = 'list-of-'
        if content_type.startswith(list_prefix):

            gen = testutils.random.gen_by_name(content_type[len(list_prefix):])

            for list_len in range(n):
                content = [gen() for _ in range(list_len)]
                await perform_access_with_content(etcd, content)

        else:

            for _ in range(n):
                gen = testutils.random.gen_by_name(content_type)
                await perform_access_with_content(etcd, gen())


async def perform_modifications(etcd, key='*', exclude=None, n=64,
                                block_size=4):

    from asyncio import gather

    def expand_key(key):
        key
        for _ in range(key.count('*')):
            key = key.replace('*', testutils.random.random_hex(exclude), 1)
        return key

    for _ in range(n // block_size):

        coro = [(etcd.root / 'test' / expand_key(key)).set(
            testutils.random.random_string()) for _ in range(block_size)]

        print(coro)

        await gather(*coro)


async def watch_etcd(etcd, n=None):

    if n is None:
        n = -1

    if n is 0:
        return

    async with etcd.subscribe() as sub:

        async for event in sub:
            print(event)

            n = n - 1
            print(n)
            if n == 0:
                return

async def test_events_node(n=256):

    from asyncio import ensure_future, sleep

    async with Etcd() as etcd:
        task = ensure_future(watch_etcd(etcd, n))
        await sleep(0.1)
        await perform_modifications(etcd, n=n)
        await task

if __name__ == '__main__':

    #for content_type in ['str', 'int', 'float', 'dict', 'list-of-str',
    #                     'list-of-str', 'list-of-int', 'list-of-float',
    #                     'list-of-dict']:
    #    run(test_access(content_type), f'access with {content_type}')

    run(test_events_node(), 'Event on a node')

    print('exit')
