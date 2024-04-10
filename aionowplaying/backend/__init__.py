import sys

from aionowplaying.backend.base import BaseNowPlayingBackend
from aionowplaying.backend.linux import LinuxNowPlayingBackend
from aionowplaying.interface import MPInterface

BACKENDS = [LinuxNowPlayingBackend]


def create_backend(interface: MPInterface) -> BaseNowPlayingBackend:
    system = sys.platform
    for cls in BACKENDS:
        if system in cls.target_platforms():
            return cls(interface)
    raise NotImplementedError
