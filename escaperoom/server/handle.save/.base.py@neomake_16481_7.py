from ...event import EventFunnel
from aiohttp import web


class WebHandler(EventFunnel):

    def __init__(self):
        super().__init__()
        self.app = web.Application()
