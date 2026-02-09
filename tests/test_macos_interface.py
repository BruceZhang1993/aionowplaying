import asyncio
import os
import sys
from datetime import datetime, timedelta
from types import SimpleNamespace

import pytest

from aionowplaying.interface.base import PlaybackProperties, PlaybackPropertyName, PlaybackStatus, PropertyName, \
    TrackListPropertyName


pytestmark = pytest.mark.skipif(sys.platform != "darwin", reason="macOS-only tests")


def _ensure_app_ready():
    # Best-effort: initialize a GUI app and give the run loop a chance.
    from Cocoa import NSApplication
    from Foundation import NSRunLoop, NSDate

    NSApplication.sharedApplication()
    run_loop = NSRunLoop.currentRunLoop()
    run_loop.runUntilDate_(NSDate.dateWithTimeIntervalSinceNow_(0.05))

if sys.platform == "darwin":
    macos_module = pytest.importorskip("aionowplaying.interface.macos")
else:
    macos_module = None


@pytest.mark.asyncio
async def test_create_handler_executes_task():
    macos = macos_module
    called = {"count": 0}

    async def handler():
        called["count"] += 1

    wrapped = macos.create_handler(None, handler)
    wrapped(None)
    await asyncio.sleep(0)
    assert called["count"] == 1


def test_set_playback_properties_metadata_and_status():
    macos = macos_module
    _ensure_app_ready()
    it = macos.MacOSInterface("test")

    meta = PlaybackProperties.MetadataBean()
    meta.title = "Song"
    meta.artist = ["Artist1", "Artist2"]
    meta.album = "Album"
    meta.albumArtist = ["Album Artist"]
    meta.composer = ["Composer"]
    meta.genre = ["Genre1"]
    meta.trackNumber = 2
    meta.duration = 30_000_000

    it.set_playback_property(PlaybackPropertyName.Metadata, meta)
    info = it.info_center.nowPlayingInfo()

    assert info[macos.MPMediaItemPropertyTitle] == "Song"
    assert info[macos.MPMediaItemPropertyArtist] == "Artist1, Artist2"
    assert info[macos.MPMediaItemPropertyAlbumTitle] == "Album"
    assert info[macos.MPMediaItemPropertyAlbumArtist] == "Album Artist"
    assert info[macos.MPMediaItemPropertyComposer] == "Composer"
    assert info[macos.MPMediaItemPropertyGenre] == "Genre1"
    if getattr(macos, "MPMediaItemPropertyAlbumTrackNumber", None) is not None:
        assert info[macos.MPMediaItemPropertyAlbumTrackNumber] == 2
    assert info[macos.MPMediaItemPropertyPlaybackDuration] == 30

    it.set_playback_property(PlaybackPropertyName.Position, 5_000_000)
    it.set_playback_property(PlaybackPropertyName.Duration, 30_000_000)

    info = it.info_center.nowPlayingInfo()
    assert info[macos.MPNowPlayingInfoPropertyElapsedPlaybackTime] == 5
    assert info[macos.MPMediaItemPropertyPlaybackDuration] == 30

    it.set_playback_property(PlaybackPropertyName.Rate, 1.25)
    info = it.info_center.nowPlayingInfo()
    assert info[macos.MPNowPlayingInfoPropertyPlaybackRate] == 1.25

    it.set_playback_property(PlaybackPropertyName.PlaybackStatus, PlaybackStatus.Paused)
    info = it.info_center.nowPlayingInfo()
    assert info[macos.MPNowPlayingInfoPropertyPlaybackRate] == 0
    playback_state = (
        it.info_center.playbackState()
        if callable(it.info_center.playbackState)
        else it.info_center.playbackState
    )
    assert playback_state == macos.MPMusicPlaybackStatePaused

    it.set_playback_property(PlaybackPropertyName.PlaybackStatus, PlaybackStatus.Playing)
    playback_state = (
        it.info_center.playbackState()
        if callable(it.info_center.playbackState)
        else it.info_center.playbackState
    )
    assert playback_state == macos.MPMusicPlaybackStatePlaying


def test_get_playback_property():
    macos = macos_module
    _ensure_app_ready()
    it = macos.MacOSInterface("test")

    it.set_playback_property(PlaybackPropertyName.Position, 2_000_000)
    it.set_playback_property(PlaybackPropertyName.Rate, 1.5)

    assert it.get_playback_property(PlaybackPropertyName.Position) == 2
    assert it.get_playback_property(PlaybackPropertyName.Rate) == 1.5


def test_property_and_tracklist_roundtrip():
    macos = macos_module
    _ensure_app_ready()
    it = macos.MacOSInterface("test")

    it.set_property(PropertyName.CanQuit, True)
    it.set_tracklist_property(TrackListPropertyName.CanEditTracks, True)

    assert it.get_property(PropertyName.CanQuit) is True
    assert it.get_tracklist_property(TrackListPropertyName.CanEditTracks) is True


def _read_enabled(command):
    value = command.enabled
    return value() if callable(value) else value


@pytest.mark.asyncio
async def test_remote_command_handlers_and_enabling():
    macos = macos_module
    _ensure_app_ready()

    class TestInterface(macos.MacOSInterface):
        def __init__(self, name: str):
            super().__init__(name)
            self.calls = []

        async def on_set_position(self, _track_id, position):
            self.calls.append(("set_position", position))

        async def on_seek(self, position):
            self.calls.append(("seek", position))

        async def on_rate(self, rate):
            self.calls.append(("rate", rate))

        async def on_loop_status(self, status):
            self.calls.append(("loop", status))

        async def on_shuffle(self, shuffle):
            self.calls.append(("shuffle", shuffle))

    it = TestInterface("test")
    it.set_playback_property(PlaybackPropertyName.CanSeek, True)
    it.set_playback_property(PlaybackPropertyName.CanControl, True)
    it.set_playback_property(PlaybackPropertyName.CanPlay, True)
    it.set_playback_property(PlaybackPropertyName.CanPause, True)
    it.set_playback_property(PlaybackPropertyName.CanGoNext, True)
    it.set_playback_property(PlaybackPropertyName.CanGoPrevious, True)

    assert _read_enabled(it.cmd_center.playCommand()) is True
    assert _read_enabled(it.cmd_center.pauseCommand()) is True
    assert _read_enabled(it.cmd_center.nextTrackCommand()) is True
    assert _read_enabled(it.cmd_center.previousTrackCommand()) is True

    if it._cmd_change_position is not None:
        assert _read_enabled(it._cmd_change_position) is True
        await it._handle_change_playback_position(SimpleNamespace(positionTime=12.5))

    if it._cmd_change_rate is not None:
        await it._handle_change_playback_rate(SimpleNamespace(playbackRate=1.25))

    if it._cmd_change_repeat is not None and macos.MPRepeatTypeOne is not None:
        await it._handle_change_repeat_mode(SimpleNamespace(repeatType=macos.MPRepeatTypeOne))

    if it._cmd_change_shuffle is not None and macos.MPShuffleTypeItems is not None:
        await it._handle_change_shuffle_mode(SimpleNamespace(shuffleType=macos.MPShuffleTypeItems))

    assert ("set_position", 12_500_000) in it.calls
    assert ("seek", 12_500_000) in it.calls
    assert ("rate", 1.25) in it.calls
    if macos.MPRepeatTypeOne is not None:
        assert any(call[0] == "loop" for call in it.calls)
    if macos.MPShuffleTypeItems is not None:
        assert ("shuffle", True) in it.calls
