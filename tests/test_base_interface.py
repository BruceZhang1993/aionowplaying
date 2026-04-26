import pytest

from aionowplaying.interface.base import BaseInterface, PlaybackStatus, PlaybackProperties, PropertyName, \
    PlaybackPropertyName, TrackListPropertyName


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


def test_base_property_storage_roundtrip():
    it = BaseInterface("base")
    it.set_property(PropertyName.CanQuit, True)
    it.set_playback_property(PlaybackPropertyName.Volume, 0.25)
    it.set_tracklist_property(TrackListPropertyName.CanEditTracks, True)

    assert it.get_property(PropertyName.CanQuit) is True
    assert it.get_playback_property(PlaybackPropertyName.Volume) == 0.25
    assert it.get_tracklist_property(TrackListPropertyName.CanEditTracks) is True


@pytest.mark.asyncio
async def test_base_tracklist_methods_default_values():
    it = BaseInterface("base")

    result = await it.on_get_tracks_metadata(["/track/1"])

    assert result == []
    await it.on_add_track("file:///song.mp3", "/org/mpris/MediaPlayer2/TrackList/NoTrack", False)
    await it.on_remove_track("/track/1")
    await it.on_goto("/track/1")
    await it.track_added(PlaybackProperties.MetadataBean(id_="/track/1"), "/org/mpris/MediaPlayer2/TrackList/NoTrack")
    await it.track_removed("/track/1")
    await it.track_list_replaced(["/track/1"], "/track/1")
    await it.track_metadata_changed("/track/1", PlaybackProperties.MetadataBean(id_="/track/1"))


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
