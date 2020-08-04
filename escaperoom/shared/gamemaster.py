def random_name(exclude=None, length=8):

    from random import choices
    from string import ascii_letters, digits

    exclude = exclude or set()
    name = ''.join(choices(ascii_letters + digits, k=length))

    if name in exclude:
        return random_name(exclude=exclude, length=length)

    return name


class GamemasterCatalog:

    def __init__(self, etcd):
        self.etcd = etcd
        self.root = etcd.root / 'gamemasters'

    async def __aiter__(self):
        async for node in self.root / '*':
            yield Gamemaster(self, node.name)

    async def get(self, gamemaster_id):

        gamemaster = Gamemaster(self.etcd, gamemaster_id)

        if not await gamemaster.exists():
            raise KeyError(gamemaster_id)

        return gamemaster

    # TODO use locks to avoid collision during creation
    async def new(self, *args, **kwargs):
        existing_gamemaster_ids = {gm.id async for gm in self}
        name = random_name(exclude=existing_gamemaster_ids)
        gamemaster = Gamemaster(self, name)
        await gamemaster.set(*args, **kwargs)
        return gamemaster


class Gamemaster:

    def __init__(self, catalog, gamemaster_id):
        self.accessor = catalog.root / gamemaster_id

    @property
    def id(self):
        return self.accessor.name

    async def set(self, firstname, lastname, email):
        await self.accessor.set({
            'firstname': firstname,
            'lastname': lastname,
            'email': email,
        })

    async def get(self):
        return await self.accessor.get()

    async def delete(self):
        await self.accessor.delete()

    async def exists(self):
        await self.accessor.exists()

    def __repr__(self):
        return f'<{type(self).__name__} {self.id}>'
