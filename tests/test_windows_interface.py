from datetime import timedelta
import asyncio
import threading
import time
import sys
from types import SimpleNamespace

import pytest

from aionowplaying.interface.base import PlaybackProperties, PlaybackPropertyName, PlaybackStatus, LoopStatus, \
    PropertyName, TrackListPropertyName


pytestmark = pytest.mark.skipif(sys.platform != "win32", reason="Windows-only tests")

if sys.platform == "win32":
    windows_module = pytest.importorskip("aionowplaying.interface.windows")
else:
    windows_module = None

def _ensure_event_loop():
    try:
        asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)


def test_set_playback_properties_and_metadata():
    windows = windows_module
    _ensure_event_loop()

    class TestInterface(windows.WindowsInterface):
        def __init__(self):
            super().__init__("test")
            self.play_calls = 0

        def on_play(self):
            self.play_calls += 1

    it = TestInterface()

    it.set_playback_property(PlaybackPropertyName.CanControl, True)
    it.set_playback_property(PlaybackPropertyName.CanPlay, True)
    it.set_playback_property(PlaybackPropertyName.CanPause, True)
    it.set_playback_property(PlaybackPropertyName.CanGoNext, True)
    it.set_playback_property(PlaybackPropertyName.CanGoPrevious, True)
    it.set_playback_property(PlaybackPropertyName.CanSeek, True)

    meta = PlaybackProperties.MetadataBean()
    meta.title = "Song"
    meta.artist = ["Artist"]
    meta.album = "Album"
    meta.albumArtist = ["Album Artist"]
    meta.genre = ["Rock", "Pop"]
    meta.id_ = "id1"
    meta.duration = 120000000
    meta.cover = "http://example.com/cover.jpg"

    it.set_playback_property(PlaybackPropertyName.Metadata, meta)
    assert it._updater.music_properties.title == "Song"
    assert it._updater.music_properties.artist == "Artist"
    assert it._updater.music_properties.album_title == "Album"
    if hasattr(it._updater.music_properties, "album_artist"):
        assert it._updater.music_properties.album_artist == "Album Artist"
    assert it._updater.thumbnail is not None
    assert it._timeline.max_seek_time is not None

    it.set_playback_property(PlaybackPropertyName.PlaybackStatus, PlaybackStatus.Playing)
    assert it._playback_properties.PlaybackStatus == PlaybackStatus.Playing
    it.set_playback_property(PlaybackPropertyName.PlaybackStatus, PlaybackStatus.Paused)
    assert it._playback_properties.PlaybackStatus == PlaybackStatus.Paused
    it.set_playback_property(PlaybackPropertyName.PlaybackStatus, PlaybackStatus.Stopped)
    assert it._playback_properties.PlaybackStatus == PlaybackStatus.Stopped

    it.set_playback_property(PlaybackPropertyName.Shuffle, True)
    assert it._controls.shuffle_enabled is True

    it.set_playback_property(PlaybackPropertyName.Rate, 1.5)
    assert it._controls.playback_rate == 1.5

    it.set_playback_property(PlaybackPropertyName.LoopStatus, LoopStatus.Track)
    assert it._playback_properties.LoopStatus == LoopStatus.Track
    it.set_playback_property(PlaybackPropertyName.LoopStatus, LoopStatus.Playlist)
    assert it._playback_properties.LoopStatus == LoopStatus.Playlist
    it.set_playback_property(PlaybackPropertyName.LoopStatus, LoopStatus.None_)
    assert it._playback_properties.LoopStatus == LoopStatus.None_

    it.set_playback_property(PlaybackPropertyName.Position, 5000000)
    assert it._timeline.position is not None

    it.set_playback_property(PlaybackPropertyName.Duration, 10000000)
    assert it._timeline.end_time is not None

    it.set_playback_property(PlaybackPropertyName.Volume, 0.4)
    assert it._playback_properties.Volume == 0.4
    it.set_playback_property(PlaybackPropertyName.MinimumRate, 0.75)
    it.set_playback_property(PlaybackPropertyName.MaximumRate, 1.5)
    assert it._playback_properties.MinimumRate == 0.75
    assert it._playback_properties.MaximumRate == 1.5


def test_event_handlers_and_buttons():
    windows = windows_module
    _ensure_event_loop()

    class TestInterface(windows.WindowsInterface):
        def __init__(self):
            super().__init__("test")
            self.called = []

        def on_play(self):
            self.called.append("play")

        def on_pause(self):
            self.called.append("pause")

        def on_next(self):
            self.called.append("next")

        def on_previous(self):
            self.called.append("previous")

        def on_stop(self):
            self.called.append("stop")

        def on_seek(self, _):
            self.called.append("seek")

        def on_set_position(self, _track_id, _pos):
            self.called.append("set_position")

        def on_shuffle(self, _):
            self.called.append("shuffle")

        def on_rate(self, _):
            self.called.append("rate")

        def on_volume(self, _):
            self.called.append("volume")

        def on_loop_status(self, _):
            self.called.append("loop")

    it = TestInterface()
    it.set_playback_property(PlaybackPropertyName.CanPlay, True)
    it.set_playback_property(PlaybackPropertyName.CanPause, True)
    it.set_playback_property(PlaybackPropertyName.CanGoNext, True)
    it.set_playback_property(PlaybackPropertyName.CanGoPrevious, True)
    it.set_playback_property(PlaybackPropertyName.CanControl, True)
    it.set_playback_property(PlaybackPropertyName.CanSeek, True)

    it.button_pressed(None, SimpleNamespace(button=windows.SystemMediaTransportControlsButton.PLAY))
    it.button_pressed(None, SimpleNamespace(button=windows.SystemMediaTransportControlsButton.PAUSE))
    it.button_pressed(None, SimpleNamespace(button=windows.SystemMediaTransportControlsButton.NEXT))
    it.button_pressed(None, SimpleNamespace(button=windows.SystemMediaTransportControlsButton.PREVIOUS))
    it.button_pressed(None, SimpleNamespace(button=windows.SystemMediaTransportControlsButton.STOP))

    it.shuffle_change_requested(None, SimpleNamespace(requested_shuffle_enabled=True))
    it.playback_rate_change_requested(None, SimpleNamespace(requested_playback_rate=1.25))
    it.property_changed(None, SimpleNamespace(property=windows.SystemMediaTransportControlsProperty.SOUND_LEVEL))

    it.playback_position_change_requested(
        None,
        SimpleNamespace(requested_playback_position=timedelta(seconds=10, microseconds=500)),
    )

    it.auto_repeat_mode_change_requested(
        None,
        SimpleNamespace(requested_auto_repeat_mode=windows.MediaPlaybackAutoRepeatMode.LIST),
    )

    assert "play" in it.called
    assert "pause" in it.called
    assert "next" in it.called
    assert "previous" in it.called
    assert "stop" in it.called
    assert "shuffle" in it.called
    assert "rate" in it.called
    assert "volume" in it.called
    assert "seek" in it.called
    assert "set_position" in it.called
    assert "loop" in it.called


def test_property_changed_non_sound_level_ignored():
    windows = windows_module
    _ensure_event_loop()

    class TestInterface(windows.WindowsInterface):
        def __init__(self):
            super().__init__("test")
            self.called = []

        def on_volume(self, _):
            self.called.append("volume")

    it = TestInterface()
    it.property_changed(None, SimpleNamespace(property=object()))
    assert it.called == []


def test_windows_property_and_tracklist_roundtrip():
    windows = windows_module
    _ensure_event_loop()
    it = windows.WindowsInterface("test")

    it.set_property(PropertyName.CanQuit, True)
    it.set_tracklist_property(TrackListPropertyName.CanEditTracks, True)

    assert it.get_property(PropertyName.CanQuit) is True
    assert it.get_tracklist_property(TrackListPropertyName.CanEditTracks) is True


def test_playback_rate_change_rejects_out_of_range():
    windows = windows_module
    _ensure_event_loop()

    class TestInterface(windows.WindowsInterface):
        def __init__(self):
            super().__init__("test")
            self.called = False

        def on_rate(self, _):
            self.called = True

    it = TestInterface()
    it.set_playback_property(PlaybackPropertyName.MinimumRate, 0.5)
    it.set_playback_property(PlaybackPropertyName.MaximumRate, 1.5)
    it.playback_rate_change_requested(None, SimpleNamespace(requested_playback_rate=2.0))

    assert it.called is False
    assert it._playback_properties.Rate != 2.0


def test_playback_position_ignored_when_cannot_seek():
    windows = windows_module
    _ensure_event_loop()

    class TestInterface(windows.WindowsInterface):
        def __init__(self):
            super().__init__("test")
            self.called = []

        def on_seek(self, _):
            self.called.append("seek")

        def on_set_position(self, *_):
            self.called.append("set_position")

    it = TestInterface()
    it.set_playback_property(PlaybackPropertyName.CanSeek, False)
    it.playback_position_change_requested(
        None,
        SimpleNamespace(requested_playback_position=timedelta(seconds=5)),
    )

    assert "seek" not in it.called
    assert "set_position" not in it.called


def test_button_pressed_respects_capabilities():
    windows = windows_module
    _ensure_event_loop()

    class TestInterface(windows.WindowsInterface):
        def __init__(self):
            super().__init__("test")
            self.called = []

        def on_play(self):
            self.called.append("play")

    it = TestInterface()
    it.set_playback_property(PlaybackPropertyName.CanPlay, False)
    it.button_pressed(None, SimpleNamespace(button=windows.SystemMediaTransportControlsButton.PLAY))

    assert "play" not in it.called


def test_auto_repeat_mode_variants():
    windows = windows_module
    _ensure_event_loop()

    class TestInterface(windows.WindowsInterface):
        def __init__(self):
            super().__init__("test")
            self.called = []

        def on_loop_status(self, value):
            self.called.append(value)

    it = TestInterface()
    it.auto_repeat_mode_change_requested(
        None,
        SimpleNamespace(requested_auto_repeat_mode=windows.MediaPlaybackAutoRepeatMode.TRACK),
    )
    it.auto_repeat_mode_change_requested(
        None,
        SimpleNamespace(requested_auto_repeat_mode=windows.MediaPlaybackAutoRepeatMode.NONE),
    )

    assert LoopStatus.Track in it.called
    assert LoopStatus.None_ in it.called


def test_run_task_from_non_main_thread():
    windows = windows_module
    _ensure_event_loop()
    loop = asyncio.get_event_loop()
    loop_started = threading.Event()

    class TestInterface(windows.WindowsInterface):
        def __init__(self):
            super().__init__("test")
            self.done = False

        async def _mark(self):
            self.done = True

    it = TestInterface()

    def loop_runner():
        asyncio.set_event_loop(loop)
        loop_started.set()
        loop.run_forever()

    loop_thread = threading.Thread(target=loop_runner)
    loop_thread.start()
    loop_started.wait(timeout=1)

    def worker():
        it._run_task(it._mark())

    thread = threading.Thread(target=worker)
    thread.start()
    thread.join()

    for _ in range(50):
        if it.done:
            break
        time.sleep(0.01)

    loop.call_soon_threadsafe(loop.stop)
    loop_thread.join(timeout=1)
    assert it.done is True


def test_stop_sets_running_flag():
    windows = windows_module
    _ensure_event_loop()
    it = windows.WindowsInterface("test")
    assert it._running is True
    asyncio.get_event_loop().run_until_complete(it.stop())
    assert it._running is False


def test_playback_position_updates_without_duration():
    windows = windows_module
    _ensure_event_loop()
    it = windows.WindowsInterface("test")

    it.set_playback_property(PlaybackPropertyName.Duration, 0)
    it.set_playback_property(PlaybackPropertyName.Position, 2_000_000)
    assert it._playback_properties.Position == 2_000_000


def test_update_metadata_media_types():
    windows = windows_module
    _ensure_event_loop()
    it = windows.WindowsInterface("test")

    meta = PlaybackProperties.MetadataBean()
    meta.title = "Image"
    meta.artist = ["Artist"]
    meta.album = "Album"
    meta.id_ = "id-image"
    meta.duration = 1_000_000
    meta.media_type = windows.MediaType.Image
    it.set_playback_property(PlaybackPropertyName.Metadata, meta)
    assert it._updater.type == windows.MediaPlaybackType.IMAGE

    meta.media_type = windows.MediaType.Video
    it.set_playback_property(PlaybackPropertyName.Metadata, meta)
    assert it._updater.type == windows.MediaPlaybackType.VIDEO
