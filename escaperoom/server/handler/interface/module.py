import logging
from pathlib import Path
from aiohttp import web
from .. import to_json


LOGGER = logging.getLogger(__name__)


class ModuleError(Exception):
    pass


class ModuleInvalidPath(ModuleError):

    def __init__(self, dirpath):
        super().__init__(f'{dirpath} is not a directory')


class ModuleMissingInitFileError(ModuleError):

    def __init__(self, filepath):
        super().__init__(f'Missing init file {filepath}')


class ModuleInvalidInitFileError(ModuleError):

    def __init__(self, filepath):
        super().__init__(f'Failed to load init file {filepath}')


class ModuleIncompleteInitFileError(ModuleError):

    def __init__(self, filepath, key):
        super().__init__(f'Missing {key} in init file {filepath}')


class Module:

    INIT_FILENAME = '__init__.json'

    def __init__(self, rootdir, dirpath):

        self.rootdir = rootdir
        self.path = Path(dirpath)

        if not self.path.is_dir():
            raise ModuleInvalidPath(self.path)

    @classmethod
    def iter_valid_dir(cls, dirpath):

        for path in Path(dirpath).iterdir():
            if path.is_dir() and (path / cls.INIT_FILENAME).is_file():
                yield path

    @classmethod
    def load_modules(cls, dirpath, factory, id_prefix='', sort=False):

        submodules = dict()

        for path in cls.iter_valid_dir(dirpath):

            try:
                submodules[id_prefix + path.name] = factory(path)

            except ModuleError as e:
                LOGGER.warning(f'Failed to load module {path}: {e}')

            except BaseException:
                LOGGER.exception(f'Failed to load module {path}', path)

        if sort:

            from collections import OrderedDict

            submodules = sorted(submodules.values(),
                                key=lambda t: int(t.id.split('-')[0]))
            return OrderedDict([(m.id, m) for m in submodules])

        return submodules

    def read_init_file(self):

        import json

        filepath = self.path / self.INIT_FILENAME

        try:
            with open(filepath) as f:
                return json.load(f)

        except FileNotFoundError:
            raise ModuleMissingInitFileError(filepath)

        except json.JSONDecodeError:
            raise ModuleInvalidInitFileError(filepath)

        except BaseException:
            raise ModuleError(self.path)


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

        self.events.add_event_source(periodic_event())

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