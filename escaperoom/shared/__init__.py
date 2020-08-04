from .etcd import Etcd

class SharedData:

    def __init__(self, etcd):

        from .gamemaster import GamemasterCatalog

        self.etcd = etcd
        self.gamemasters = GamemasterCatalog(etcd)
