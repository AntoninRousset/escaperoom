import logging


LOGGER = logging.getLogger(__name__)


class ScriptHandler(WebHandler):

    DIRPATH = 'scripts/'

    def __init__(self, context, rootdir):

        super().__init__(context, rootdir)
        self.router.add_get('/{name}.mjs', self.get_script)

    async def get_script(self, request):

        from aiohttp.web import FileResponse

        name = request.match_info['name']

        path = str(self.rootdir / self.DIRPATH / f'{name}.mjs')
        resp = FileResponse(path)
        resp.headers['Content-Type'] = 'application/javascript'
        return resp
