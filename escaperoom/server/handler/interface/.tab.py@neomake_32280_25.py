import logging
from pathlib import Path
from aiohttp import web
from .module import Module, ModuleIncompleteInitFileError
from .. import to_json


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
            self.content = self.path / data['content']

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

    TAB_DIR = 'tabs/'

    def __init__(self, rootdir):

        super().__init__()

        self.rootdir = Path(rootdir)

        self.router.add_get('', self.get_all_tabs)
        self.router.add_get('/{group_id}.{tab_id}/content',
                            self.get_tab_content)
        self.router.add_get('/{group_id}.{tab_id}/script',
                            self.get_tab_script)

    async def get_all_tabs(self, request):

        tabs_dir = self.rootdir / self.TAB_DIR
        tabs = Module.load_modules(tabs_dir,
                                   lambda p: TabGroup(self.rootdir, p),
                                   sort=True)

        return web.Response(content_type='application/json',
                            text=to_json(list(tabs.values())))

    async def get_tab_content(self, request):
        tab = self._get_tab_from_request(request)
        return web.FileResponse(tab.path / tab.content)

    async def get_tab_script(self, request):
        tab = self._get_tab_from_request(request)

        if tab.script:
            return web.FileResponse(tab.path / tab.script)

        return web.Response(content_type='application/javascript', text='')

    def _get_tab_from_request(self, request):

        group_id = request.match_info['group_id']
        tab_id = request.match_info['tab_id']

        return Tab(self.rootdir,
                   self.rootdir / self.TAB_DIR / group_id / tab_id)
