import logging
from pathlib import Path
from aiohttp import web
from . import to_json


LOGGER = logging.getLogger(__name__)


class InterfaceHandler(web.Application):

    def __init__(self, events, rootdir):

        super().__init__()

        self.rootdir = Path(rootdir)

        self.events = events

        async def periodic_event():

            from asyncio import sleep

            while True:
                print('--- sending ---')
                yield 'salut'
                await sleep(1)

        self.events.add_source(periodic_event())

        self.router.add_subapp('/tabs',
                               TabsHandler())

        self.router.add_get('/tabs', self.get_tabs)
        self.router.add_get('/tab/{group_id}.{tab_id}', self.get_tab)
        #self.router.add_get('/widgets', self.get_widgets)
        #self.router.add_get('/widget/{widget}', self.get_widget)

    async def get_tabs(self, request):

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
