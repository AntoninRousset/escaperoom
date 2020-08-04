import logging
from pathlib import Path
from aiohttp import web


LOGGER = logging.getLogger(__name__)


class IconsHandler(web.Application):

    DIRPATH = 'icons/'

    def __init__(self, rootdir):

        super().__init__()
        self.rootdir = Path(rootdir)

        self.router.add_get('/{name}.css', self.get_style)

    async def get_style(self, request):

        name = request.match_info['name']

        print('*** get style', name)

        path = str(self.rootdir / self.DIRPATH / f'{name}.css')
        resp = web.FileResponse(path)
        resp.headers['Content-Type'] = 'text/css'
        return resp
