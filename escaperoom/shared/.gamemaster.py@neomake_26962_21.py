class GamemasterCatalog:

    def __init__(self, etcd):
        self.etcd = etcd
        self.root = etcd.root / 'gamemasters'

    async def __aiter__(self):
        pass

    async def get(self, gamemaster_id):

        gamemaster = Gamemaster(self.etcd, gamemaster_id)

        if not await gamemaster.exists():
            raise KeyError(gamemaster_id)

        return gamemaster


class Gamemaster:

    def __init__(self, catalog, gamemaster_id):
        self.catalog = catalog
        self.id = str(gamemaster_id)

    async def exists(self):
        await (self.catalog / self.id).exists()
