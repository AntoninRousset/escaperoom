#!/usr/bin/env python
# -*- coding: utf-8 -*-

from collections import defaultdict


class Registered:

    _register = defaultdict(set)

    def __init__(self):
        self._register[self.__class__].add(self)

    @property
    def register(self):
        reg = self._register[self.__class__].copy()
        for c in self.__class__.__subclasses__():
            reg = reg.union(self._register[c])
        return reg
