import logging
from pathlib import Path
from aiohttp import web

from .tab import TabHandler
from .style import StyleHandler
from .script import ScriptHandler
from .icon import IconHandler

LOGGER = logging.getLogger(__name__)


class InterfaceHandler(web.Application):

    def __init__(self, events, rootdir):

        super().__init__()

        self.rootdir = Path(rootdir)

        self.events = events

        self.add_subapp('/tabs', TabHandler(self.rootdir))
        self.add_subapp('/styles', StyleHandler(self.rootdir))
        self.add_subapp('/scripts', ScriptHandler(self.rootdir))
        self.add_subapp('/icons', IconHandler(self.rootdir))
