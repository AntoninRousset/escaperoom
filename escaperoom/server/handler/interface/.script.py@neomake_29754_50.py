import logging
from pathlib import Path
from aiohttp import web
from . import to_json


LOGGER = logging.getLogger(__name__)


class ScriptHandler(web.Application):

    DIRPATH = 'scripts/'

    def __init__(self, rootdir):

        super().__init__()
        self.rootdir = Path(rootdir)

        self.router.add_get('/{name}.js', self.get_script)

    async def get_script(self, request):
        name = request.match_info['name']
        path = str(self.rootdir / self.DIRPATH / f'{name}.js')
        return web.FileResponse(path)
