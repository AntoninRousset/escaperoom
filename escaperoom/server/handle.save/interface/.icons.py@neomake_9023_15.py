import logging
from pathlib import Path
from aiohttp import web


LOGGER = logging.getLogger(__name__)


class IconsHandler(web.Application):

    DIRPATH = 'icons/'

    def __init__(self, rootdir):

        super().__init__()
        self.rootdir = Path(rootdir)

        self.router.add_get('/{filename}', self.get_style)

    async def get_style(self, request):

        filename = request.match_info['filename']

        path = str(self.rootdir / self.DIRPATH / filename)
        resp = web.FileResponse(path)
        resp.headers['Content-Type'] = 'text/css'
        return resp
