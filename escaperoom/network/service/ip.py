#!/usr/bin/env python
# -*- coding: utf-8 -*-


def get_interfaces():
    import netifaces as ni
    return ni.interfaces()


def get_addresses(interfaces='all', ip_version='all'):

    import netifaces as ni
    from ipaddress import ip_address

    if interfaces == 'all':
        interfaces = get_interfaces()

    interfaces = {interface: ni.ifaddresses(interface)
                  for interface in interfaces}

    ip_version = {
        'ipv4': {ni.AF_INET},
        'ipv6': {ni.AF_INET6},
        'all': {ni.AF_INET, ni.AF_INET6},
    }[str(ip_version).lower()]

    return {ip_address(address['addr'].split('%')[0])
            for interface in interfaces.values()
            for version in (interface.keys() & ip_version)
            for address in interface[version]}
