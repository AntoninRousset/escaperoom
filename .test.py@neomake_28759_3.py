#!/usr/bin/env python
# -*- coding: utf-8 -*-

from escaperoom.shared import etcd
import asyncio

async def test(cluster):

    print('-- test started --')

    async with cluster.subscribe():
        print('-- subscribed --')

    await asyncio.sleep(2)
    print('-- test finished --')


async def main():

    print('-- main started --')

    cluster = etcd.EtcdCluster()
    task = asyncio.ensure_future(test(cluster))
    await asyncio.sleep(8)
    task.cancel()
    await cluster.client.close()
    print('-- main finished --')



if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
