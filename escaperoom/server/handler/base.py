from ...event import EventFunnel
from aiohttp import web


class WebHandler(EventFunnel):

    def __init__(self, context, rootdir):

        from pathlib import Path

        super().__init__()

        self.context = context
        self.app = web.Application()
        self.rootdir = Path(rootdir)

    def add_subhandler(self, prefix, handler):
        self.app.add_subapp(prefix, handler.app)
        self.add_event_source(handler)
