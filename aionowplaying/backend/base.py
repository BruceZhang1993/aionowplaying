from abc import ABCMeta, abstractmethod
from typing import List

from aionowplaying.interface import MPInterface, MPPlayerInterface


class BaseNowPlayingBackend(metaclass=ABCMeta):
    @staticmethod
    @abstractmethod
    def target_platforms() -> List[str]:
        pass

    def __init__(self, interface: MPInterface, player_interface: MPPlayerInterface):
        self._interface = interface
        self._player_interface = player_interface

    @abstractmethod
    def run(self):
        pass

    @abstractmethod
    def destroy(self):
        pass
