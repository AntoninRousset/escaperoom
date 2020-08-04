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


class EtcdGamemasters(EtcdAccessor):

    def __init__(self, root):
        super().__init__(root, 'gamemaster')


class EtcdCluster(EtcdNode):

    FILEPATH = Path('/tmp/escaperoom.etcd')

    def __init__(self):

        super().__init__(self, '/')
        self.db = SharedFile(self.FILEPATH)

        self.gamemasters = EtcdGamemasters(self.root)

    async def get_value(self, nodepath):

        from json import dump

        async with self.db:
            await self._lag()


    async def _emul_lag(self, max_ms=100, min_ms=0):

        from random import randint
        from asyncio import sleep

        await sleep(randint(min_ms, max_ms) / 1000)




class SharedFile:

    def __init__(self, path):

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
        
