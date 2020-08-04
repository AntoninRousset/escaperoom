from ..event import EventSource
from weakref import ref
from pathlib import Path


class EtcdInstance(dict):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class EtcdAccessor(EventSource):

    def __init__(self, root):
        super().__init__()
        self._root = ref(root)

    @property
    def root(self):
        return self._root()

    def open(self):
        return EtcdSession(self)

    async def pull(self):
        return EtcdInstance()

    async def push(self, instance):
        pass


class EtcdNode(EtcdAccessor):

    def __init__(self, root, subdir):
        super().__init__(root)
        self.subdir = Path(subdir)


class EtcdSession:

    def __init__(self, accessor):
        self.accessor = accessor
        self.instance = None

    async def __aenter__(self):
        self.instance = self.accessor.pull()
        return self.instance

    async def __aexit__(self, exc_type, exc_value, traceback):
        if self.instance is not None:
            await self.accessor.push(self.instance)


class EtcdGamemasters(EtcdNode):

    def __init__(self, root):
        super().__init__(root, 'gamemaster')


class EtcdCluster(EtcdNode):

    FILEPATH = Path('/tmp/escaperoom.etcd')

    def __init__(self):

        super().__init__(self, '/')
        self.db = SharedFile(self.FILEPATH)

        self.gamemasters = EtcdGamemasters(self.root)

    async def get_value(self, nodepath=None):
        nodepath = nodepath or self.subdir
        data = await self._load_data()
        return data[nodepath]

    async def set_value(self, value, nodepath=None):
        nodepath = nodepath or self.subdir
        data = await self._load_data()
        data[nodepath] = value

    async def get_subnodes(self, nodepath=None):
        nodepath = nodepath or self.subdir
        data = await self._load_data()
        return data.subnodes(nodepath)

    async def _load_data(self):

        from json import load

        async with self.db as f:

            await self._emul_lag()
            return FileData(load(f))

    async def _dump_data(self, data):

        from json import dump

        async with self.db as f:

            await self._emul_lag()
            return dump(f, data.data)

    async def _emul_lag(self, max_ms=100, min_ms=0):

        from random import randint
        from asyncio import sleep

        await sleep(randint(min_ms, max_ms) / 1000)


class SharedFile:

    def __init__(self, path, mode='r'):

        from asyncio import Lock

        self.path = path
        self.lock = Lock()
        self.file = None

    async def __aenter__(self):
        await self.lock.acquire()
        self.file = open(self.path, 'r+')
        return self.file

    async def __aexit__(self, exc_type, exc, tb):
        if self.file is not None:
            self.file.close()
            self.file = None
        self.lock.release()


class FileData():

    def __init__(self, *args, **kwargs):
        from collections import defaultdict
        self.data = defaultdict(dict, *args, **kwargs)

    def __getitem__(self, k):
        return self.data[str(k)]

    def __setitem__(self, k, v):
        self.data[str(k)] = v

    def subnodes(self, nodepath='/'):
        return {k.split('/')[0] for k in self.subtree(nodepath)} 

    def subtree(self, nodepath='/'):
        nodepath = str(nodepath)
        if not nodepath.endswith('/'):
            nodepath = nodepath + '/'
        subtree = filter(lambda x: x.startswith(nodepath), self.data.keys())
        return (k[len(nodepath):] for k in subtree)
