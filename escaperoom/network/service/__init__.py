#!/usr/bin/env python
# -*- coding: utf-8 -*-

# requierments:
#   - dev-python/zeroconf
#   - dev-python/netifaces

import logging

SERVICE_TYPE = 'escaperoom'
logger = logging.getLogger(__name__)


# TODO more a etcd service?
class EscaperoomUnitService:

    # default port checked on Wikipedia "List of TCP and UDP port numbers" for
    # conflict
    def __init__(self, name=None, interfaces='all', ip_version='all',
                 port=15451):

        from zeroconf import Zeroconf, ServiceInfo, IPVersion
        from .ip import get_interfaces, get_addresses

        logger.debug(f'Creating a new service with name: {name}, '
                          f'interfaces: {interfaces}, ip_version: '
                          f'{ip_version}, port: {port}')

        if interfaces == 'all':
            interfaces = get_interfaces()
        self.zeroconf = Zeroconf(
            ip_version={
                'all': IPVersion.All,
                'ipv4': IPVersion.V4Only,
                'ipv6': IPVersion.V6Only,
            }[ip_version.lower()])

        self.name = name
        if self.name is None:
            from socket import gethostname
            self.name = 'escaperoom ' + (gethostname() or 'Unknown computer')
            logger.debug(f'Default service name: {name}')

        # TODO what to put inside?
        properties = {}

        type_qualname = f'_{SERVICE_TYPE}._tcp.local.'
        addresses = [addr.packed for addr in get_addresses(interfaces,
                                                           ip_version)]
        self.info = ServiceInfo(type_qualname, f'{self.name}.{type_qualname}',
                                addresses=addresses,
                                port=port,
                                properties=properties)
        logger.info(f'Service "{self.name}" created')
        logger.debug(f'Default service name: {self.name}')

    def start(self):
        logger.debug(f'Service "{self.name}" starting')
        self.zeroconf.register_service(self.info)
        logger.info(f'Service "{self.name}" started')

    def stop(self):
        logger.debug(f'Service "{self.name}" stoping')
        self.zeroconf.unregister_service(self.info)
        logger.info(f'Service "{self.name}" stopped')

    def __del__(self):
        self.stop()


class EscaperoomUnitDiscovery:

    def __init__(self, ip_version='all'):
        self.ip_version = ip_version.lower()
        self.zeroconf = None
        logger.info(f'Service discovery created')
        available = dict()


    def start(self):

        from zeroconf import Zeroconf, IPVersion, ServiceBrowser

        self.zeroconf = Zeroconf(
            ip_version={
                'all': IPVersion.All,
                'ipv4': IPVersion.V4Only,
                'ipv6': IPVersion.V6Only,
            }[self.ip_version])

        type_qualname = f'_{SERVICE_TYPE}._tcp.local.'
        self.browser = ServiceBrowser(self.zeroconf, type_qualname, self)
        logger.info(f'Service discovery started')

    def stop(self):
        if self.zeroconf:
            self.zeroconf.close()

    def add_service(self, zeroconf, type, name):
        name = name.split('.')[0]
        logger.debug(f'Service found: "{name}"')

    def remove_service(self, zeroconf, type, name):
        name = name.split('.')[0]
        logger.debug(f'Service lost: "{name}"')
