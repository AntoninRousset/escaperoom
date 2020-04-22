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
from base64 import b64decode
from collections import defaultdict

from . import asyncio, Network

from ..subprocess import SubProcess


class Cluster(Network):

    class _Etcdctl():

        def __init__(self, *args, env=dict(), wait_terminate=False):
            self.args = ['etcdctl', '--write-out=json', *args]
            self.env = {'ETCDCTL_API': '3'}
            self.env.update(env)
            self.wait_terminate = wait_terminate

            self.sp = None

        def __await__(self):
            return self.__aenter__().__await__()

        async def __aenter__(self):
            if self.sp is None or self.sp.poll() is not None:
                self.sp = await asyncio.create_subprocess_exec(
                    *self.args, env=self.env,
                    stdin=asyncio.subprocess.PIPE,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE,  # TODO
                    )
            return self

        async def __aexit__(self, exc_type, exc, tb):
            w = self.terminate()
            if self.wait_terminate:
                await w

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
            return data

        async def communicate(self, msg=None):
            if msg is None:
                line = (await self.sp.communicate())[0]
            else:
                line = (await self.sp.communicate(input=msg.encode()))[0]
            return self._decode(line)

        async def responses(self):
            while True:
                yield self._decode(await self.sp.stdout.readline())

        def terminate(self):
            try:
                self.sp.terminate()
            except ProcessLookupError:
                pass
            return asyncio.create_task(self.sp.wait())

    class Lock():

        _underlying_locks = defaultdict(asyncio.Lock)

        def __init__(self, key, *, wait_release=False):
            self.key = Cluster.normalize_key(key)
            self.wait_release = wait_release

            self._client = None
            self._alive = asyncio.Event()
            # asyncio.create_task(self._watching(self.lock_key))

        async def __aenter__(self):
            await self.acquire()

        async def __aexit__(self, exc_type, exc, tb):
            w = self.release()
            if self.wait_release:
                await w

        async def _watching(self, lock_key):
            ttl = None
            async for lease_id in Cluster.watch(lock_key, timeout=ttl):
                print('lease_id:', lease_id)
                if lease_id is None:
                    self._alive.clear()
                else:
                    sp = await asyncio.create_subprocess_exec(
                        *(Cluster.CLIENT_EXEC['args']), 'lease', 'timetolive',
                        lease_id,
                        stdout=asyncio.subprocess.PIPE,
                        env=Cluster.CLIENT_EXEC.get('env')
                        )
                    line = (await sp.communicate())[0]
                    try:
                        r = Cluster._decode_etcd_resp(line)
                        ttl = int(r['ttl'])
                    except Exception as e:
                        raise RuntimeError(f'cannot set value: {repr(e)}')

        async def acquire(self):
            async with self._underlying_lock:
                self._client = await Cluster._Etcdctl('lock', str(self.key))
                async for r in self._client.responses():
                    key, lease_id = r['kvs'][0]['key'].rsplit('/', 1)
                    if key == self.key:
                        return await Cluster.set(self.lock_key, lease_id)

        async def _release(self):
            if self._client is not None:
                await self._client.terminate()
            asyncio.create_task(Cluster.rem(self.lock_key))

        def release(self):  # TODO self.locked() and exceptions
            return asyncio.create_task(self._release())

        def locked(self):
            raise RuntimeError('Not implemented')
            # TODO? track self._lock_key

        @property
        def lock_key(self):
            return self.key + '_lock'

        @property
        def _underlying_lock(self):
            return self._underlying_locks[self.lock_key]

    class Condition():

        def __init__(self, key, lock=None):
            if lock is None:
                lock = Cluster.Lock(key)
            elif lock.key != key:
                raise ValueError('lock argument must point to the same key')

            self._underlying_condition = asyncio.Condition(lock=lock)
            self.locked = self._underlying_condition.locked
            self.acquire = self._underlying_condition.acquire
            self.release = self._underlying_condition.release

    @classmethod
    def normalize_key(cls, key):
        return key.rstrip('/') + '/'

    def __init__(self, name: str, peers, *, new=False):
        if set(Cluster.entries()):
            raise RuntimeError('There can be only one cluster running')
        super().__init__(name)

        self.peers = self._resolve_ips(peers)
        self._soon_ready = asyncio.Event()

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
            stderr=asyncio.subprocess.PIPE
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
            else:
                if re.match('.*embed: ready to serve client requests', line):
                    self._soon_ready.set()
                self._log_info(line)

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
    async def get(cls, key: str) -> str:
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
                    raise KeyError(key)
            else:
                raise KeyError(key)

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
    async def watch(cls, key, *, first=True):
        if not key:
            raise RuntimeError('key cannot be empty')

        if first:
            try:
                yield await Cluster.get(key)
            except KeyError:
                pass

        async with Cluster._Etcdctl('watch', str(key)) as client:
            async for r in client.responses():
                for event in r['Events']:
                    if 'kv' in event:
                        kv = event['kv']
                        if 'key' in kv and kv['key'] == key:
                            yield kv.get('value')

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


class Shared():

    def __init__(self, name):
        self.name = name
        self.__changed = asyncio.Condition()
        #self.__etcd_lock = Cluster.get().client.Lock(self.path)

    async def __aenter__(self):
        await self.__changed.__aenter__()
        #await asyncio.run_in_executor(None, self.__etcd_lock.acquire)
        print(self.__etcd_lock.is_acquired)

    async def __aexit__(self, exc_type, exc, tb):
        #self.__etcd_lock.release()
        await self.__changed.__aexit__(exc_type, exc, tb)

    @property
    def path(self):  # TODO
        return '/shared/' + self.name + '/'
