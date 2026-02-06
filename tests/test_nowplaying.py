import pytest

import aionowplaying as aionp


class DummyInterface(aionp.BaseInterface):
    def __init__(self):
        super().__init__("dummy")
        self.playback_updates = []

    def set_playback_property(self, name, value):
        self.playback_updates.append((name, value))


class NowPlayingFacade(DummyInterface):
    def update_playback_mode(self, loop_status: aionp.LoopStatus, shuffle: bool):
        self.set_playback_property(aionp.PlaybackPropertyName.LoopStatus, loop_status)
        self.set_playback_property(aionp.PlaybackPropertyName.Shuffle, shuffle)

    def update_song_props(self, meta: dict):
        metadata = aionp.PlaybackProperties.MetadataBean()
        metadata.artist = meta.get("artists", ["Unknown"])
        metadata.album = meta.get("album", "")
        metadata.title = meta.get("title", "")
        metadata.cover = meta.get("artwork", "")
        metadata.url = meta.get("artwork", "")
        metadata.duration = 0
        self.set_playback_property(aionp.PlaybackPropertyName.Metadata, metadata)

    def update_position(self, position):
        self.set_playback_property(aionp.PlaybackPropertyName.Position, int(position * 1000))

    def update_playback_status(self, status: aionp.PlaybackStatus):
        self.set_playback_property(aionp.PlaybackPropertyName.PlaybackStatus, status)


def test_update_song_props():
    server = NowPlayingFacade()
    server.update_song_props({
        "title": "Hello World",
        "artists": ["hello world"],
        "album": "Hello World",
        "artwork": "https://example.com/art.jpg",
    })

    name, metadata = server.playback_updates[-1]
    assert name == aionp.PlaybackPropertyName.Metadata
    assert metadata.title == "Hello World"
    assert metadata.artist == ["hello world"]
    assert metadata.album == "Hello World"
    assert metadata.cover == "https://example.com/art.jpg"
    assert metadata.url == "https://example.com/art.jpg"


def test_update_position():
    server = NowPlayingFacade()
    server.update_position(20.5)
    assert server.playback_updates[-1] == (aionp.PlaybackPropertyName.Position, 20500)


def test_update_playback_status():
    server = NowPlayingFacade()
    server.update_playback_status(aionp.PlaybackStatus.Playing)
    assert server.playback_updates[-1] == (
        aionp.PlaybackPropertyName.PlaybackStatus,
        aionp.PlaybackStatus.Playing,
    )


def test_update_playback_mode():
    server = NowPlayingFacade()
    server.update_playback_mode(aionp.LoopStatus.Playlist, True)
    server.update_playback_mode(aionp.LoopStatus.Track, False)

    assert server.playback_updates[0] == (
        aionp.PlaybackPropertyName.LoopStatus,
        aionp.LoopStatus.Playlist,
    )
    assert server.playback_updates[1] == (
        aionp.PlaybackPropertyName.Shuffle,
        True,
    )
    assert server.playback_updates[2] == (
        aionp.PlaybackPropertyName.LoopStatus,
        aionp.LoopStatus.Track,
    )
    assert server.playback_updates[3] == (
        aionp.PlaybackPropertyName.Shuffle,
        False,
    )
