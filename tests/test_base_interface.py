import pytest

from aionowplaying.interface.base import BaseInterface, PlaybackStatus, PlaybackProperties


class DummyInterface(BaseInterface):
    def __init__(self, status: PlaybackStatus):
        super().__init__("dummy")
        self._status = status
        self.play_called = False
        self.pause_called = False

    def get_playback_property(self, name):
        if name.value == "PlaybackStatus":
            return self._status
        return None

    async def on_play(self):
        self.play_called = True

    async def on_pause(self):
        self.pause_called = True


def test_metadata_defaults():
    meta = PlaybackProperties.MetadataBean()
    assert meta.title == "Unknown"
    assert meta.duration == 0
    assert meta.artist == []


@pytest.mark.asyncio
async def test_on_play_pause_calls_pause_when_playing():
    it = DummyInterface(PlaybackStatus.Playing)
    await it.on_play_pause()
    assert it.pause_called is True
    assert it.play_called is False


@pytest.mark.asyncio
async def test_on_play_pause_calls_play_when_not_playing():
    it = DummyInterface(PlaybackStatus.Paused)
    await it.on_play_pause()
    assert it.play_called is True
    assert it.pause_called is False
