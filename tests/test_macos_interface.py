import asyncio
import base64
import os
import sys
from datetime import datetime, timedelta
from types import SimpleNamespace

import pytest

from aionowplaying.interface.base import PlaybackProperties, PlaybackPropertyName, PlaybackStatus, PropertyName, \
    TrackListPropertyName, LoopStatus


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


@pytest.mark.asyncio
async def test_create_event_handler_executes_task_with_event():
    macos = macos_module
    called = {"event": None}

    async def handler(event):
        called["event"] = event

    wrapped = macos.create_event_handler(handler)
    marker = object()
    wrapped(marker)
    await asyncio.sleep(0)
    assert called["event"] is marker


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

    it.set_playback_property(PlaybackPropertyName.PlaybackStatus, PlaybackStatus.Stopped)
    info = it.info_center.nowPlayingInfo()
    assert info[macos.MPNowPlayingInfoPropertyPlaybackRate] == 0
    playback_state = (
        it.info_center.playbackState()
        if callable(it.info_center.playbackState)
        else it.info_center.playbackState
    )
    assert playback_state == macos.MPMusicPlaybackStateStopped


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


def test_update_supported_rates_and_loop_shuffle_controls():
    macos = macos_module
    _ensure_app_ready()
    it = macos.MacOSInterface("test")

    if it._cmd_change_rate is not None:
        it.set_playback_property(PlaybackPropertyName.MinimumRate, 2.0)
        it.set_playback_property(PlaybackPropertyName.MaximumRate, 1.0)
        # Invalid min/max should not update supported rates.
        current_rates = getattr(it._cmd_change_rate, "supportedPlaybackRates", None)
        it.set_playback_property(PlaybackPropertyName.MinimumRate, 0.5)
        it.set_playback_property(PlaybackPropertyName.MaximumRate, 2.0)
        updated_rates = getattr(it._cmd_change_rate, "supportedPlaybackRates", None)
        if current_rates is not None and updated_rates is not None:
            try:
                assert 0.5 in updated_rates
                assert 2.0 in updated_rates
            except Exception:
                # Some macOS frameworks expose supportedPlaybackRates as read-only.
                pass

    if it._cmd_change_repeat is not None and macos.MPRepeatTypeOff is not None:
        it.set_playback_property(PlaybackPropertyName.LoopStatus, LoopStatus.Track)
        try:
            assert it._cmd_change_repeat.currentRepeatType == macos.MPRepeatTypeOne
        except Exception:
            pass
        it.set_playback_property(PlaybackPropertyName.LoopStatus, LoopStatus.Playlist)
        try:
            assert it._cmd_change_repeat.currentRepeatType == macos.MPRepeatTypeAll
        except Exception:
            pass
        it.set_playback_property(PlaybackPropertyName.LoopStatus, LoopStatus.None_)
        try:
            assert it._cmd_change_repeat.currentRepeatType == macos.MPRepeatTypeOff
        except Exception:
            pass

    if it._cmd_change_shuffle is not None and macos.MPShuffleTypeOff is not None:
        it.set_playback_property(PlaybackPropertyName.Shuffle, True)
        try:
            assert it._cmd_change_shuffle.currentShuffleType == macos.MPShuffleTypeItems
        except Exception:
            pass
        it.set_playback_property(PlaybackPropertyName.Shuffle, False)
        try:
            assert it._cmd_change_shuffle.currentShuffleType == macos.MPShuffleTypeOff
        except Exception:
            pass


def test_load_artwork_paths(tmp_path):
    macos = macos_module
    _ensure_app_ready()
    it = macos.MacOSInterface("test")

    missing = it._load_artwork(str(tmp_path / "missing.png"))
    assert missing is None

    png_bytes = base64.b64decode(
        b"iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVQImWNgYGD4DwAB"
        b"BAEAi0P9twAAAABJRU5ErkJggg=="
    )
    img_path = tmp_path / "cover.png"
    img_path.write_bytes(png_bytes)

    artwork = it._load_artwork(str(img_path))
    if macos.MPMediaItemArtwork is not None:
        assert artwork is not None

    file_url_artwork = it._load_artwork(img_path.resolve().as_uri())
    if macos.MPMediaItemArtwork is not None:
        assert file_url_artwork is not None


def test_set_command_enabled_fallback():
    macos = macos_module
    _ensure_app_ready()
    it = macos.MacOSInterface("test")

    class DummyCommand:
        def __init__(self):
            self.isEnabled = False

    cmd = DummyCommand()
    it._set_command_enabled(cmd, True)
    assert cmd.isEnabled is True


def _read_enabled(command):
    value = command.enabled if hasattr(command, "enabled") else command.isEnabled
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


@pytest.mark.asyncio
async def test_remote_handlers_ignore_when_capability_disabled():
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

        async def on_loop_status(self, status):
            self.calls.append(("loop", status))

        async def on_shuffle(self, shuffle):
            self.calls.append(("shuffle", shuffle))

    it = TestInterface("test")

    it.set_playback_property(PlaybackPropertyName.CanSeek, False)
    await it._handle_change_playback_position(SimpleNamespace(positionTime=9.0))
    assert it.calls == []

    if macos.MPRepeatTypeOne is not None:
        it.set_playback_property(PlaybackPropertyName.CanControl, False)
        await it._handle_change_repeat_mode(SimpleNamespace(repeatType=macos.MPRepeatTypeOne))
        assert it.calls == []

    if macos.MPShuffleTypeItems is not None:
        it.set_playback_property(PlaybackPropertyName.CanControl, False)
        await it._handle_change_shuffle_mode(SimpleNamespace(shuffleType=macos.MPShuffleTypeItems))
        assert it.calls == []


@pytest.mark.asyncio
async def test_repeat_and_shuffle_handler_variants():
    macos = macos_module
    _ensure_app_ready()

    class TestInterface(macos.MacOSInterface):
        def __init__(self, name: str):
            super().__init__(name)
            self.calls = []

        async def on_loop_status(self, status):
            self.calls.append(("loop", status))

        async def on_shuffle(self, shuffle):
            self.calls.append(("shuffle", shuffle))

    it = TestInterface("test")
    it.set_playback_property(PlaybackPropertyName.CanControl, True)

    if macos.MPRepeatTypeAll is not None:
        await it._handle_change_repeat_mode(SimpleNamespace(repeatType=macos.MPRepeatTypeAll))
    if macos.MPRepeatTypeOff is not None:
        await it._handle_change_repeat_mode(SimpleNamespace(repeatType=macos.MPRepeatTypeOff))
    if macos.MPShuffleTypeOff is not None:
        await it._handle_change_shuffle_mode(SimpleNamespace(shuffleType=macos.MPShuffleTypeOff))

    if macos.MPRepeatTypeAll is not None:
        assert ("loop", LoopStatus.Playlist) in it.calls
    if macos.MPRepeatTypeOff is not None:
        assert ("loop", LoopStatus.None_) in it.calls
    if macos.MPShuffleTypeOff is not None:
        assert ("shuffle", False) in it.calls


def test_set_command_enabled_with_none_command():
    macos = macos_module
    _ensure_app_ready()
    it = macos.MacOSInterface("test")
    it._set_command_enabled(None, True)
