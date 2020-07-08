import logging
from pathlib import Path
from aiohttp import web


LOGGER = logging.getLogger(__name__)


class IconHandler(web.Application):

    DIRPATH = 'icons/'

    def __init__(self, rootdir):

        super().__init__()
        self.rootdir = Path(rootdir)

        self.router.add_get('/{name}.svg', self.get_style)

    async def get_style(self, request):

        name = request.match_info['name']

        path = str(self.rootdir / self.DIRPATH / f'{name}.svg')
        resp = web.FileResponse(path)
        resp.headers['Content-Type'] = 'image/svg+xml'
        return resp
