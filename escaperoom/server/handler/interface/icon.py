import logging
from ..base import WebHandler


LOGGER = logging.getLogger(__name__)


class IconHandler(WebHandler):

    DIRPATH = 'icons/'

    def __init__(self, context, rootdir):

        super().__init__(context, rootdir)
        self.app.router.add_get('/{name}.svg', self.get_icon)

    async def get_icon(self, request):

        from aiohttp.web import FileResponse

        name = request.match_info['name']

        path = str(self.rootdir / self.DIRPATH / f'{name}.svg')
        resp = FileResponse(path)
        resp.headers['Content-Type'] = 'image/svg+xml'
        return resp