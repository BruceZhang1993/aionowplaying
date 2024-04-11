import pytest

from aionowplaying.service import NowPlayingService
from example_interface import ExampleMPInterface


class TestNowPlayingService:
    def __init__(self):
        self._it = ExampleMPInterface()
        self._service = NowPlayingService(self._it)
