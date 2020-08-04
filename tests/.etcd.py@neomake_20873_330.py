#!/usr/bin/env python
# -*- coding: utf-8 -*-

from pathlib import Path
from sys import path
path.insert(0, str(Path(__file__).absolute().parent.parent))


import testutils
from testutils import run, TestError
from escaperoom.shared.etcd import Etcd


async def perform_access_with_content(etcd, content, n=3):

    node = etcd.root / 'test' / testutils.random.random_hex()

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


async def perform_modifications(etcd, key, exclude=None, n=64,
                                chunk_size=4, deadtime=0.05):

    from asyncio import gather, sleep

    key = str(key)

    def expand_key(key):
        for _ in range(key.count('*')):
            key = key.replace('*', testutils.random.random_hex(exclude), 1)
        return key

    random_values = [testutils.random.random_string() for _ in range(n)]

    for i in range(0, n, chunk_size):

        chunk_values = random_values[i:i + chunk_size]
        await gather(*[(etcd.root / expand_key(key)).set(v)
                       for v in chunk_values])

        await sleep(deadtime)

    return random_values


async def record_event_source(source):

    from asyncio import CancelledError

    record = []

    try:
        async with source.subscribe() as sub:

            async for event in sub:
                record.append(event)

    except CancelledError:
        return record


async def perform_event_test(etcd, source, valid, invalid=None):

    from asyncio import ensure_future, gather, sleep

    task = ensure_future(record_event_source(source))
    await sleep(0.1)

    records = await gather(*valid, *invalid)
    emitted = {val for rec in records[:len(valid)] for val in rec}

    task.cancel()
    received = {event.value for event in await task}

    if emitted != received:
        raise TestError('Wrong data')


async def test_events_node(n=256):

    async with Etcd() as etcd:

        node_name = testutils.random.random_hex()
        node = etcd.root / 'test' / node_name

        perform_event_test(etcd, node, [
            perform_modifications(etcd, node.key, n=n),
        ], [
            perform_modifications(etcd, 'test/*', exclude={node_name}, n=n),
            perform_modifications(etcd, 'test/{node_name}/*', n=n),
            perform_modifications(etcd, 'test/*/*', n=n),
        ])


async def test_events_subtree(n=256):

    async with Etcd() as etcd:

        node_name = testutils.random.random_hex()
        node = etcd.root / 'test' / node_name

        perform_event_test(etcd, node, [
            perform_modifications(etcd, node.key, n=n),
            perform_modifications(etcd, 'test/{node_name}/*', n=n),
            perform_modifications(etcd, 'test/{node_name}/*/*', n=n),
        ], [
            perform_modifications(etcd, 'test/*', exclude={node_name}, n=n),
            perform_modifications(etcd, 'test/*/*', exclude={node_name}, n=n),
            
        ])



async def test_events_node(n=256):

    from asyncio import ensure_future, gather, sleep

    async with Etcd() as etcd:

        node_name = testutils.random.random_hex()
        node = etcd.root / 'test' / node_name

        task = ensure_future(record_event_source(node))
        await sleep(0.1)

        emitted, _, _ = await gather(
            perform_modifications(etcd, node.key, n=n),
            perform_modifications(etcd, 'test/*', exclude=node_name, n=n),
            perform_modifications(etcd, f'test/{node_name}/*', n=n),
            perform_modifications(etcd, f'test/*/*', n=n),
        )
        emitted = set(emitted)

        task.cancel()
        received = {event.value for event in await task}

        if emitted != received:
            raise TestError('Wrong data')





if __name__ == '__main__':

    #for content_type in ['str', 'int', 'float', 'dict', 'list-of-str',
    #                     'list-of-str', 'list-of-int', 'list-of-float',
    #                     'list-of-dict']:
    #    run(test_access(content_type), f'access with {content_type}')

    run(test_events_node(), 'event on a single node')
