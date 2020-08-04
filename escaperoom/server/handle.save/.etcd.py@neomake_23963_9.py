#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
from . import to_json
from .base import WebHandler


logger = logging.getLogger(__name__)


class EtcdHandler(WebHandler):

    def __init__(self, context):

        super().__init__(context)
        self.app.router.add_get('tree/{selector:.*}',
                                self.get_tree)

    def get_tree(self, request):

        from aiohttp.web import Response

        return Response(content_type='application/json',
                        text=to_json(units))
