from datetime import timedelta
import asyncio
import sys
from types import SimpleNamespace

import pytest

from aionowplaying.interface.base import PlaybackProperties, PlaybackPropertyName, PlaybackStatus, LoopStatus


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
    meta.id_ = "id1"
    meta.duration = 120000000
    meta.cover = "http://example.com/cover.jpg"

    it.set_playback_property(PlaybackPropertyName.Metadata, meta)
    assert it._updater.music_properties.title == "Song"
    assert it._updater.music_properties.artist == "Artist"
    assert it._updater.music_properties.album_title == "Album"
    assert it._updater.thumbnail is not None
    assert it._timeline.max_seek_time is not None

    it.set_playback_property(PlaybackPropertyName.PlaybackStatus, PlaybackStatus.Playing)
    assert it._playback_properties.PlaybackStatus == PlaybackStatus.Playing

    it.set_playback_property(PlaybackPropertyName.Shuffle, True)
    assert it._controls.shuffle_enabled is True

    it.set_playback_property(PlaybackPropertyName.Rate, 1.5)
    assert it._controls.playback_rate == 1.5

    it.set_playback_property(PlaybackPropertyName.LoopStatus, LoopStatus.Track)
    assert it._playback_properties.LoopStatus == LoopStatus.Track

    it.set_playback_property(PlaybackPropertyName.Position, 5000000)
    assert it._controls._timeline.position is not None

    it.set_playback_property(PlaybackPropertyName.Duration, 10000000)
    assert it._controls._timeline.end_time is not None


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
