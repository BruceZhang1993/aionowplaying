import sys

from aionowplaying.backend.base import BaseNowPlayingBackend
from aionowplaying.backend.linux import LinuxNowPlayingBackend
from aionowplaying.interface import MPInterface, MPPlayerInterface, MPTrackListInterface

BACKENDS = [LinuxNowPlayingBackend]


def create_backend(interface: MPInterface, player_interface: MPPlayerInterface,
                   tracklist_interface: MPTrackListInterface) -> BaseNowPlayingBackend:
    system = sys.platform
    for cls in BACKENDS:
        if system in cls.target_platforms():
            return cls(interface, player_interface, tracklist_interface)
    raise NotImplementedError
