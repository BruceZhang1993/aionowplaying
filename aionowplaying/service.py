from threading import Thread

from aionowplaying.backend import create_backend
from aionowplaying.interface import MPInterface


class NowPlayingService(Thread):
    def __init__(self, interface: MPInterface):
        super().__init__()
        self._interface = interface
        self._backend = create_backend(interface)

    def run(self):
        pass
