#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging

SERVICE_TYPE = 'escaperoom'


# TODO more a etcd service?
class EscaperoomService:

    logger = logging.getLogger(__name__)

    # default port checked on Wikipedia "List of TCP and UDP port numbers" for
    # conflict
    def __init__(self, name=None, interfaces='all', ip_version='all',
                 port=15451):

        from zeroconf import Zeroconf, ServiceInfo, IPVersion
        from .ip import get_interfaces, get_addresses

        self.logger.debug(f'Creating a new service with name: {name}, '
                          f'interfaces: {interfaces}, ip_version: ',
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
            self.logger.debug(f'Default service name: {name}')

        # TODO what to put inside?
        properties = {}

        type_qualname = f'_{SERVICE_TYPE}._tcp.local.'
        addresses = [addr.packed for addr in get_addresses(interfaces,
                                                           ip_version)]
        self.info = ServiceInfo(type_qualname, f'{name}.{type_qualname}',
                                addresses=addresses,
                                port=port,
                                properties=properties)
        self.logger.info(f'Service "{name}" created')
        self.logger.debug(f'Default service name: {name}')

    def start(self):
        self.logger.debug(f'Service "{self.name}" starting')
        self.zeroconf.register_service(self.info)
        self.logger.info(f'Service "{self.name}" started')

    def stop(self):
        self.logger.debug(f'Service "{self.name}" stoping')
        self.zeroconf.register_service(self.info)
        self.logger.info(f'Service "{self.name}" stopped')

    def __del__(self):
        self.stop()
