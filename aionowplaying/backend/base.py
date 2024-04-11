from abc import ABCMeta, abstractmethod
from typing import List

from aionowplaying.interface import MPInterface, MPPlayerInterface, MPTrackListInterface
from aionowplaying.model import Metadata


class BaseNowPlayingBackend(metaclass=ABCMeta):
    @staticmethod
    @abstractmethod
    def target_platforms() -> List[str]:
        pass

    def __init__(self, interface: MPInterface, player_interface: MPPlayerInterface,
                 tracklist_interface: MPTrackListInterface):
        self._interface = interface
        self._player_interface = player_interface
        self._tracklist_interface = tracklist_interface

    def seeked(self, position: int):
        pass

    def tracklist_replaced(self, tracks: List[str], current: str):
        pass

    def track_added(self, metadata: Metadata, after_track: str):
        pass

    def track_removed(self, track: str):
        pass

    def track_metadata_changed(self, track: str, metadata: Metadata):
        pass

    @abstractmethod
    def run(self):
        pass

    @abstractmethod
    def destroy(self):
        pass
