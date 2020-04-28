'''
 This program is free software: you can redistribute it and/or modify
 it under the terms of the GNU General Public License as published by
 the Free Software Foundation, version 3.
 This program is distributed in the hope that it will be useful, but
 WITHOUT ANY WARRANTY; without even the implied warranty of
 MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
 General Public License for more details.
 You should have received a copy of the GNU General Public License
 along with this program. If not, see <http://www.gnu.org/licenses/>.
'''

import json
import re
from base64 import b64encode, b64decode

from . import asyncio, Network

from ..subprocess import SubProcess


class Cluster(Network):

    class _Etcdctl():

        # TODO? TXN
        # TODO wait for the server to be ready

        def __init__(self, *args, env=dict()):
            self.args = ['etcdctl', '--write-out=json', *args]
            self.env = {'ETCDCTL_API': '3'}
            self.env.update(env)

            self.sp = None

        def __await__(self):
            return self.__aenter__().__await__()

        async def __aenter__(self):
            if not self.running():
                self.sp = await asyncio.create_subprocess_exec(
                    *self.args, env=self.env,
                    stdin=asyncio.subprocess.PIPE,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE,  # TODO
                    )
            return self

        async def __aexit__(self, exc_type, exc, tb):
            self.terminate()

        def _decode(self, resp):
            def decode_kv(kv):
                if 'key' in kv:
                    kv['key'] = b64decode(kv['key']).decode()
                if 'value' in kv:
                    kv['value'] = b64decode(kv['value']).decode()
            data = json.loads(resp)
            if 'kvs' in data:
                for kv in data['kvs']:
                    decode_kv(kv)
            if 'Events' in data:
                for event in data['Events']:
                    if 'kv' in event:
                        decode_kv(event['kv'])
                    if 'prev_kv' in event:
                        decode_kv(event['prev_kv'])
            return data

        async def communicate(self, msg=None):
            if msg is None:
                line = (await self.sp.communicate())[0]
            else:
                line = (await self.sp.communicate(input=msg.encode()))[0]
            return self._decode(line)

        async def responses(self, *, timeout=None):
            while True:
                p = self.sp.stdout
                line = await asyncio.wait_for(p.readline(), timeout=timeout)
                try:
                    if line:
                        yield self._decode(line)
                except json.JSONDecodeError:
                    print(f'could not decode response: {line}')
                    print(await self.sp.stderr.read())

        def terminate(self):
            try:
                self.sp.terminate()
            except ProcessLookupError:
                pass
            asyncio.create_task(self.sp.wait())

        def running(self):
            return self.sp is not None and self.sp.returncode is None

    @classmethod
    def normalize_key(cls, key):
        return key.rstrip('/') + '/'

    def __init__(self, name: str, peers, *, new=False, arm64=False):
        if set(Cluster.entries()):
            raise RuntimeError('There can be only one cluster running')
        super().__init__(name)

        self.peers = self._resolve_ips(peers)
        self._soon_ready = asyncio.Event()

        self.env = dict()
        if arm64:
            self.env['ETCD_UNSUPPORTED_ARCH'] = 'arm64'

        asyncio.run_until_complete(self._start(new))  # TODO don't run the loop

        print('STARTED')

    async def _start(self, new):

        import shutil
        try:
            shutil.rmtree('/tmp/escaperoom.etcd')
        except FileNotFoundError:
            pass
        except Exception as e:
            self._log_warning(f'Cannot clear etcd dir: {e}')

        sp = SubProcess(
            'cluster',
            'etcd',
            '--name', self.name,
            '--data-dir', '/tmp/escaperoom.etcd',  # TODO relevant dir
            '--initial-advertise-peer-urls', self._etcd_advertise_peer_urls,
            '--initial-cluster-state', 'new' if new else 'existing',
            '--listen-peer-urls', self._etcd_listen_peer_urls,
            '--listen-client-urls', self._etcd_listen_client_urls,
            '--advertise-client-urls', self._etcd_advertise_peer_urls,
            '--initial-cluster', self._etcd_cluster,
            stderr=asyncio.subprocess.PIPE,
            env=self.env
            )

        await sp.running
        asyncio.create_task(self._listen(sp.stderr))

        import requests
        while True:
            try:
                await self._soon_ready.wait()
                await asyncio.sleep(2)  # TODO, mmmh
                return requests.get('http://127.0.0.1:2379/version',
                                    timeout=0.3, verify=False)
            except Exception:
                self._log_warning('failed to connect to etcd server')

    async def _listen(self, pipe):
        import json
        while True:
            line = (await pipe.readline()).decode()
            if str.startswith(line, '{'):  # for >=etcd-3.4.0
                data = json.loads(line)

                if data['msg'] == 'now serving peer/client/metrics':
                    self._soon_ready.set()
                elif data['msg'] == 'request cluster ID mismatch':
                    self._log_error('cluster is not the same on every device')

                if data['level'] == 'debug':
                    self._log_debug(data['msg'])
                elif data['level'] == 'info':
                    self._log_info(data['msg'])
                elif data['level'] == 'warn':
                    self._log_warning(data['msg'])
            elif line != '':
                if re.match('.*embed: ready to serve client requests', line):
                    self._soon_ready.set()
                elif re.match('.*etcd on unsupported platform.*', line):
                    self._log_error('etcd failed to start: wrong architecture')

    # TODO discovery, DNS
    def _resolve_ips(self, peers):
        while True:
            import socket
            from urllib.parse import urlparse, urlunparse
            ips = dict()
            try:
                for name, url in peers.items():
                    p = urlparse(url)
                    if not p.scheme:
                        p = urlparse('http://'+url)
                    netloc = f'{socket.gethostbyname(p.hostname)}:{p.port}'
                    ips[name] = urlunparse((p[0], netloc, p[2], p[3], p[4],
                                            p[5]))
                return ips
            except socket.gaierror as e:
                self._log_warning(f'could not resolve url "{url}": {e}')
                import time
                time.sleep(5)
        return ips

    @classmethod
    async def set(cls, key: str, value: str):
        if not key:
            raise RuntimeError('key cannot be empty')
        if not value:
            raise RuntimeError('value cannot be empty')

        async with Cluster._Etcdctl('put', '--', str(key)) as client:
            try:
                await client.communicate(str(value))
            except Exception as e:
                raise RuntimeError(f'cannot set value: {repr(e)}')

    @classmethod
    async def get(cls, key: str, default=None) -> str:
        if not key:
            raise RuntimeError('key cannot be empty')

        async with Cluster._Etcdctl('get', '--', str(key)) as client:
            try:
                r = await client.communicate()
                for kv in r['kvs']:
                    if 'key' in kv and 'value' in kv:
                        if kv['key'] == key:
                            return kv['value']
            except KeyError as e:
                if e.args[0] == 'kvs':
                    return default
            else:
                raise RuntimeError('Bad response')

    @classmethod
    async def rem(cls, key: str):
        if not key:
            raise RuntimeError('key cannot be empty')

        async with Cluster._Etcdctl('del', '--', str(key)) as client:
            try:
                await client.communicate()
            except Exception as e:
                raise RuntimeError(f'cannot remove value: {repr(e)}')

    @classmethod
    async def lock(cls, key: str):
        client = await Cluster._Etcdctl('lock', key)
        async for r in client.responses():
            rkey, lease_id = r['kvs'][0]['key'].rsplit('/', 1)
            if rkey == key:
                return client, lease_id

    @classmethod
    async def watch(cls, key: str, default=None, *, first=True, timeout=None):
        if not key:
            raise RuntimeError('key cannot be empty')

        async with Cluster._Etcdctl('watch', '--prev-kv', str(key)) as client:
            if first:
                try:
                    yield await Cluster.get(key, default=default), default
                except KeyError:
                    pass

            async for r in client.responses(timeout=timeout):
                for event in r['Events']:
                    if 'kv' in event:
                        if 'prev_kv' in event:
                            prev_kv = event['prev_kv']
                            if 'key' in prev_kv and prev_kv['key'] == key:
                                value = prev_kv.get('value')
                                old = default if value is None else value
                        else:
                            old = default
                        kv = event['kv']
                        if 'key' in kv and kv['key'] == key:
                            value = kv.get('value')
                            yield default if value is None else value, old

    @property
    def _etcd_listen_client_urls(self):
        return self._etcd_advertise_client_urls + ',http://127.0.0.1:2379'

    @property
    def _etcd_advertise_client_urls(self):
        words = self._etcd_advertise_peer_urls.split(':', 2)
        return words[0] + ':' + words[1] + ':2379'  # TODO better

    @property
    def _etcd_advertise_peer_urls(self):
        return f'{self.peers[self.name]}'

    @property
    def _etcd_listen_peer_urls(self):
        return f'{self.peers[self.name]}'

    @property
    def _etcd_cluster(self):
        peers = list()
        for name, uri in self.peers.items():
            peers.append(f'{name}={uri}')
        return ','.join(peers)


class Lock():

    class _Common():

        def __init__(self, key, *, loop=None):
            self.lock_key = key + '_lock'
            self._ordering_lock = asyncio.Lock(loop=loop)

            self._lease_id = None
            self._locked = asyncio.Event(loop=loop)

            asyncio.create_task(self._watching(self.lock_key))

        async def _watching(self, lock_key):
            async def read_ttl(lease_id):
                async with Cluster._Etcdctl('lease', 'timetolive',
                                            lease_id) as client:
                    async for r in client.responses():  # TODO communicate?
                        if 'ttl' in r:
                            return int(r['ttl'])
                        return None

            ttl = None
            async for lease_id, _ in Cluster.watch(lock_key, timeout=ttl):
                self._lease_id = lease_id
                if lease_id is None:
                    self._locked.clear()
                else:
                    self._locked.set()
                    ttl = await read_ttl(lease_id)

    _commons = dict()

    def __init__(self, key, *, loop=None):

        self.key = Cluster.normalize_key(key)
        self._client = None

        if self.key not in Lock._commons:
            Lock._commons[self.key] = Lock._Common(self.key, loop=loop)
        self._common = Lock._commons[self.key]

        self._loop = self._common._ordering_lock._loop

    async def __aenter__(self):
        await self.acquire()

    async def __aexit__(self, exc_type, exc, tb):
        self.release()

    async def acquire(self):
        try:
            async with self._common._ordering_lock:
                self._client, lease_id = await Cluster.lock(self.key)
                await Cluster.set(self._common.lock_key, lease_id)
                await self._common._locked.wait()
                return
        except Exception:
            if self._client is not None:
                self._client.terminate()
            raise

    async def _release(self):
        await Cluster.rem(self._common.lock_key)
        self._client.terminate()
        self._client = None
        self._common._locked.clear()

    def release(self):
        if not self.locked():
            raise RuntimeError('Cannot release unacquired lock')
        if self._client is None or not self._client.running():
            raise RuntimeError('Cannot release locked acquired by a stranger')

        asyncio.create_task(self._release())

    def locked(self):
        return self._common._locked.is_set()


class Condition:

    class _Common():

        def __init__(self, key, *, loop=None):
            self._notify_key = key + '_notify'
            self._notification = asyncio.Event(loop=loop)

            self._waiters_key = key + '_waiters'
            self._waiting_line = Lock(self._notify_key, loop=loop)

            asyncio.create_task(self._notification_watching())

        async def _notification_watching(self):
            async for notify, _ in Cluster.watch(self._notify_key, 0):
                if int(notify) > 0:
                    self._notification.set()
                else:
                    self._notification.clear()

    _commons = dict()

    def __init__(self, key, *, lock=None, loop=None):
        if loop is not None:
            self._loop = loop
        else:
            self._loop = asyncio.get_event_loop()

        if lock is None:
            lock = Lock(key, loop=loop)
        elif lock._loop is not loop:
            raise ValueError('loop argument must agree with lock')
        elif lock.key != key:
            raise ValueError('lock argument must point to the same key')

        self.key = Cluster.normalize_key(key)
        self._lock = lock

        self._notify_written = asyncio.Event()
        self._notify_written.set()

        if self.key not in Condition._commons:
            common = Condition._Common(self.key, loop=loop)
            Condition._commons[self.key] = common
        self._common = Condition._commons[self.key]

    async def __aenter__(self):
        await self.acquire()

    async def __aexit__(self, exc_type, exc, tb):
        self.release()

    async def acquire(self):
        async for notify, _ in Cluster.watch(self.notify_key, 0):
            await self._lock.acquire()
            if int(notify) == 0:
                return
            self._lock.release()

    async def wait(self):
        waiters = int(await Cluster.get(self.waiters_key, 0))
        await Cluster.set(self.waiters_key, str(waiters+1))
        self._lock.release()
        try:
            async with self._common._waiting_line:
                while True:
                    await self._common._notification.wait()
                    await self._lock.acquire()

                    notify = int(await Cluster.get(self.notify_key, 0))
                    if notify > 0:
                        await Cluster.set(self.notify_key, str(notify-1))
                        waiters = int(await Cluster.get(self.waiters_key))
                        await Cluster.set(self.waiters_key, str(waiters-1))
                        return

                    self._common._notification.clear()
        except Exception:
            await self._lock.acquire()
            raise

    async def _notify(self, n=None):
        current = int(await Cluster.get(self.notify_key, 0))
        waiters = int(await Cluster.get(self.waiters_key, 0))
        new = waiters if n is None else min(current+n, waiters)
        await Cluster.set(self._common._notify_key, str(new))
        self._notify_written.set()

    def notify(self, n=1):
        if not self._lock.locked():
            raise RuntimeError('lock not acquired')
        self._notify_written.clear()
        asyncio.create_task(self._notify(n))

    def notify_all(self):
        self.notify(None)

    async def _release(self):
        await self._notify_written.wait()
        self._lock.release()

    def release(self):
        asyncio.create_task(self._release())

    @property
    def notify_key(self):
        return self._common._notify_key

    @property
    def waiters_key(self):
        return self._common._waiters_key


class Shared:
    pass
