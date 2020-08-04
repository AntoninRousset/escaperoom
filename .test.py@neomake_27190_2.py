#!/usr/bin/env python
# -*- coding: utf-8 -*-

from escaperoom.shared import etcd
import asyncio

async def test(cluster):

    print('-- test started --')

    root = cluster.root
    await asyncio.sleep(2)
    print('-- test finished --')


async def main():

    print('-- main started --')

    cluster = etcd.EtcdCluster()
    #await test(cluster)
    await asyncio.sleep(2)
    cluster.client.close()
    print('-- main finished --')



if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
