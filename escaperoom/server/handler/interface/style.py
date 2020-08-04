import logging
from ..base import WebHandler


LOGGER = logging.getLogger(__name__)


class StyleHandler(WebHandler):

    DIRPATH = 'styles/'

    def __init__(self, context, rootdir):

        super().__init__(context, rootdir)
        self.app.router.add_get('/{name}.css', self.get_style)

    async def get_style(self, request):

        from aiohttp.web import FileResponse

        name = request.match_info['name']

        path = str(self.rootdir / self.DIRPATH / f'{name}.css')
        resp = FileResponse(path)
        resp.headers['Content-Type'] = 'text/css'
        return resp
