from threading import Thread

from aionowplaying.backend import create_backend
from aionowplaying.interface import MPInterface, MPPlayerInterface, MPTrackListInterface


class NowPlayingService(Thread):
    def __init__(self, interface: MPInterface, player_interface: MPPlayerInterface,
                 tracklist_interface: MPTrackListInterface):
        super().__init__()
        self._interface = interface
        self._backend = create_backend(interface, player_interface, tracklist_interface)

    def run(self):
        self._backend.run()

    def stop(self):
        self._backend.destroy()
