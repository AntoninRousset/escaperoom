#!/usr/bin/env python
# -*- coding: utf-8 -*-

from escaperoom.shared import etcd
import asyncio

async def test(cluster):

    print('-- test started --')

    p = cluster.root / 'xxx'

    print('/ :', [k async for k in cluster.root.subtree().keys])
    print('/xxx :', [k async for k in p.subtree().keys])

    #async with cluster.root.subtree.subscribe() as sub:
    #    async for event in sub:
    #        print('%% event %%', event)

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
