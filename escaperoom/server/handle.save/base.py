from ...event import EventFunnel
from aiohttp import web


class WebHandler(EventFunnel):

    def __init__(self, context):
        super().__init__()
        self.context = context
        self.app = web.Application()

    def add_subhandler(self, prefix, handler):
        self.app.add_subapp(handler.app) 
        self.app.add_event_source(handler)
