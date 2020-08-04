#!/usr/bin/env python
# -*- coding: utf-8 -*-

import testutils
from testutils import run, TestError
from ..escaperoom.shared import Etcd

from pathlib import Path
from sys import path
path = [str(Path(__file__).parent.parent)]


async def perform_access_with_content(etcd, content, n=3):

    key = testutils.random.random_key()
    node = etcd.root / key

    for i in range(n):
        await node.set(content)
        if not await node.exists():
            raise TestError(f'Does not exist after set {i} to {content}')
        if await node.get() != content:
            raise TestError(f'Wrong data after set {i} to {content}')

        await node.remove()
        if await node.exists():
            raise TestError(f'Exists after remove {i}')
        try:
            await node.get()
            raise TestError(f'Get does not raise exception after remove {i}')

        except KeyError:
            pass


async def test_access(content_type, n=10):

    etcd = Etcd()

    list_prefix = 'list-of-'
    if content_type.startswith(list_prefix):

        gen = testutils.random.gen_by_name(content_type[len(list_prefix):])

        for list_len in range(n):
            content = [gen() for _ in range(list_len)]
            await perform_access_with_content(etcd, content)

    else:

        for _ in range(n):
            gen = testutils.random.gen_by_name(content_type[len(list_prefix):])
            await perform_access_with_content(etcd, gen())


if __name__ == '__main__':

    for content_type in ['str', 'int', 'float', 'dict', 'list-of-str',
                         'list-of-str', 'list-of-int', 'list-of-float',
                         'list-of-dict']:
        run(test_access(content_type), content_type)
