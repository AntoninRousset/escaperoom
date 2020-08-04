#!/usr/bin/env python
# -*- coding: utf-8 -*-

from testutils import run
from ..escaperoom.shared import Etcd
import asyncio


def random_key():
    from random import randint
    key = randint(1, 1 << 64) - 1
    return f'test/{key:016x}'

def random_string(nmin=4, nmax = 32):
    from string import printable



async def test_get():
    etcd = Etcd()

    key = random_key()

    await p.set()



async def test(cluster):

    print('-- test started --')

    p = cluster.root / 'xxx'

    #print('/ :', [k async for k in cluster.root.subtree().keys])
    #print('/xxx :', [k async for k in p.subtree().keys])

    async with cluster.root.children().subscribe() as sub:
        async for event in sub:
            print('%% event %%', event)

    await asyncio.sleep(2)
    print('-- test finished --')


async def main():

    print('-- main started --')

    cluster = etcd.EtcdCluster()
    await test(cluster)
    #task = asyncio.ensure_future(test(cluster))
    #await asyncio.sleep(8)
    #task.cancel()
    await cluster.client.close()
    print('-- main finished --')



if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
