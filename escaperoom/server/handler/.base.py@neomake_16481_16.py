from ...event import EventFunnel
from aiohttp import web


class WebHandler(EventFunnel):

    def __init__(self, escaperoom_context):
        super().__init__()
        self.context = escaperoom_context
        self.app = web.Application()
