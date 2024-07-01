import pytest

from aionowplaying.service import NowPlayingService
from example_interface import ExampleMPInterface, ExampleMPPlayerInterface, ExampleMPTrackListInterface


class TestNowPlayingService:
    def __init__(self):
        self._it = ExampleMPInterface()
        self._it_player = ExampleMPPlayerInterface()
        self._it_track = ExampleMPTrackListInterface()
        self._service = NowPlayingService(self._it, self._it_player, self._it_track)
