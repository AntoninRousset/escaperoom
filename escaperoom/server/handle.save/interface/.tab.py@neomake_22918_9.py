import logging
from pathlib import Path
from aiohttp import web
from .module import Module, ModuleIncompleteInitFileError
from . import to_json


LOGGER = logging.getLogger(__name__)


class TabGroup(Module):

    def __init__(self, rootdir, dirpath):

        super().__init__(rootdir, dirpath)

        self.id = self.path.name
        data = self.read_init_file()

        try:
            self.name = data['name']

        except KeyError as e:
            raise ModuleIncompleteInitFileError(self.path, e.args[0])

        self.tabs = self.load_modules(self.path,
                                      lambda p: Tab(self.rootdir, p),
                                      f'{self.id}/', sort=True)

    def __json__(self):
        return {
            'id': self.id,
            'name': self.name,
            'tabs': list(self.tabs.values()),
        }


class Tab(Module):

    def __init__(self, rootdir, dirpath):
        super().__init__(rootdir, dirpath)

        self.id = f'{self.path.parent.name}.{self.path.name}'
        data = self.read_init_file()

        try:
            self.name = data['name']
            self.icon = self.path / data['icon']
            self.html = self.path / data['content']

        except KeyError as e:
            raise ModuleIncompleteInitFileError(self.path, e.args[0])

    def __json__(self):

        icon_path = Path('ressources') / self.icon.relative_to(self.rootdir)

        return {
            'id': self.id,
            'name': self.name,
            'icon': str(icon_path),
        }


class TabHandler(web.Application):

    def __init__(self, rootdir):

        super().__init__()

        self.rootdir = Path(rootdir)

        async def periodic_event():

            from asyncio import sleep

            while True:
                print('--- sending ---')
                yield 'salut'
                await sleep(1)

        self.events.add_source(periodic_event())

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
