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

# import etcd3_asyncio as etcd3
# from .error import EtcdNotOpenedError
import logging


logger = logging.getLogger(__name__)


class Cluster:

    def __init__(self, endpoint, *, persistent=False):

        super().__init__()

        self.persistent = persistent

        # self.client = etcd3.Client(*endpoint.split(':'))
        self.nodes = set()
        print('Cluster created')

    async def start(self):
        try:
            # k = await self.client.Range(b'a', b'b')
            # print(k)
            print('asd')
        except Exception as e:
            print('**', repr(e))
        print('started')
