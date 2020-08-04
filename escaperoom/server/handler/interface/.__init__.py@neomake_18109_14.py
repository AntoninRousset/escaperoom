import logging
from ..base import WebHandler


LOGGER = logging.getLogger(__name__)


class InterfaceHandler(WebHandler):

    def __init__(self, context, rootdir):

        from .tab import TabHandler
        from .style import StyleHandler
        from .script import ScriptHandler
        from .icon import IconHandler

        super().__init__(context, rootdir)

        args = (self.context, self.rootdir)
        self.add_subhandler('/tabs', TabHandler(*args))
        self.add_subhandler('/styles', StyleHandler(*args))
        self.add_subhandler('/scripts', ScriptHandler(*args))
        self.add_subhandler('/icons', IconHandler(*args))
