import logging
from pathlib import Path
from aiohttp import web
from . import to_json


LOGGER = logging.getLogger(__name__)


class ScriptHandler(web.Application):

    def __init__(self, rootdir):

        super().__init__()
        self.rootdir = Path(rootdir)

        self.router.add_get('/{name}.js', self.get_script)

    async def get_script(self, request):

        tabs_dir = self.rootdir / 'tabs'
        tabs = Module.load_modules(tabs_dir,
                                   lambda p: TabGroup(self.rootdir, p),
                                   sort=True)
        return web.Response(content_type='application/json',
                            text=to_json(list(tabs.values())))

    async def get_tab(self, request):

        group_id = request.match_info['group_id']
        tab_id = request.match_info['tab_id']
        tab = Tab(self.rootdir, self.rootdir / 'tabs' / group_id / tab_id)

        return web.FileResponse(tab.path / tab.html)
