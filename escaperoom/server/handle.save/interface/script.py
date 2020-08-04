import logging
from pathlib import Path
from aiohttp import web


LOGGER = logging.getLogger(__name__)


class ScriptHandler(web.Application):

    DIRPATH = 'scripts/'

    def __init__(self, rootdir):

        super().__init__()
        self.rootdir = Path(rootdir)

        self.router.add_get('/{name}.mjs', self.get_script)

    async def get_script(self, request):

        name = request.match_info['name']

        print('** get script', name)

        path = str(self.rootdir / self.DIRPATH / f'{name}.mjs')
        resp = web.FileResponse(path)
        resp.headers['Content-Type'] = 'application/javascript'
        return resp
