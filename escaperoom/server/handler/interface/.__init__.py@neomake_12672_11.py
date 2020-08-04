import logging
from ..base import WebHandler

from .tab import TabHandler
from .style import StyleHandler
from .script import ScriptHandler
from .icon import IconHandler


LOGGER = logging.getLogger(__name__)


class InterfaceHandler(WebHandler):

    def __init__(self, context):

        from pathlib import Path

        super().__init__()

        self.rootdir = Path('/')

        self.add_subhandler('/tabs', TabHandler(self.context,
                                                self.rootdir))
        self.add_subhandler('/styles', StyleHandler(self.context,
                                                    self.rootdir))
        self.add_subhandler('/scripts', ScriptHandler(self.context,
                                                      self.rootdir))
        self.add_subhandler('/icons', IconHandler(self.context,
                                                  self.rootdir))
