import logging
from .module import Module, ModuleIncompleteInitFileError
from ..base import WebHandler


LOGGER = logging.getLogger(__name__)


class TabHandler(WebHandler):

    DIRPATH = 'tabs/'

    def __init__(self, context, rootdir):

        super().__init__(context, rootdir)

        self.app.router.add_get('', self.get_all_tabs)
        self.app.router.add_get('/{group_id}.{tab_id}/icon',
                                self.get_tab_icon)
        self.app.router.add_get('/{group_id}.{tab_id}/content',
                                self.get_tab_content)
        self.app.router.add_get('/{group_id}.{tab_id}/script',
                                self.get_tab_script)

    async def get_all_tabs(self, request):

        from .. import to_json
        from aiohttp.web import Response

        tabs_dir = self.rootdir / self.DIRPATH
        tabs = Module.load_modules(tabs_dir,
                                   lambda p: TabGroup(self.rootdir, p),
                                   sort=True)

        return Response(content_type='application/json',
                        text=to_json(list(tabs.values())))

    async def get_tab_icon(self, request):
        from aiohttp.web import FileResponse
        tab = self._get_tab_from_request(request)
        return FileResponse(tab.path / tab.icon)

    async def get_tab_content(self, request):
        from aiohttp.web import FileResponse
        tab = self._get_tab_from_request(request)
        return FileResponse(tab.path / tab.content)

    async def get_tab_script(self, request):
        from aiohttp.web import Response, FileResponse
        tab = self._get_tab_from_request(request)

        if tab.script:
            return FileResponse(tab.path / tab.script)

        return Response(content_type='application/javascript', text='')

    def _get_tab_from_request(self, request):

        group_id = request.match_info['group_id']
        tab_id = request.match_info['tab_id']

        return Tab(self.rootdir,
                   self.rootdir / self.DIRPATH / group_id / tab_id)


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
            if 'script' in data:
                self.script = self.path / data['script']
            else:
                self.script = None

        except KeyError as e:
            raise ModuleIncompleteInitFileError(self.path, e.args[0])

    def __json__(self):
        return {
            'id': self.id,
            'name': self.name,
        }



