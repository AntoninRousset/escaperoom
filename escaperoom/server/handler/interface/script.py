import logging
from ..base import WebHandler


LOGGER = logging.getLogger(__name__)


class ScriptHandler(WebHandler):

    DIRPATH = 'scripts/'

    def __init__(self, context, rootdir):
        super().__init__(context, rootdir)
        self.app.router.add_get('/{filepath:.*}', self.get_script)

    async def get_script(self, request):

        from aiohttp.web import FileResponse

        filepath = request.match_info['filepath']

        if not filepath.endswith('js'):
            filepath = f'{filepath}.js'

        path = str(self.rootdir / self.DIRPATH / filepath)
        resp = FileResponse(path)
        resp.headers['Content-Type'] = 'application/javascript'
        return resp
