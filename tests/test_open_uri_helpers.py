import asyncio
import importlib
import sys
from types import ModuleType
from pathlib import Path

import pytest

SRC_ROOT = Path(__file__).resolve().parents[1] / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))


def _install_fake_frameworks(monkeypatch, url_factory, open_result=True):
    foundation = ModuleType("Foundation")
    appkit = ModuleType("AppKit")
    mediaplayer = ModuleType("MediaPlayer")

    class _FakeNSMutableDictionary(dict):
        @classmethod
        def dictionary(cls):
            return cls()

        def mutableCopy(self):
            return _FakeNSMutableDictionary(self)

    class _FakeNSURL:
        calls = []

        @staticmethod
        def URLWithString_(uri):
            _FakeNSURL.calls.append(uri)
            return url_factory(uri)

    class _FakeNSImage:
        @classmethod
        def alloc(cls):
            return cls()

        def initWithContentsOfURL_(self, _):
            return self

        def size(self):
            return (0, 0)

    class _FakeWorkspace:
        def __init__(self):
            self.opened_urls = []

        def openURL_(self, url):
            self.opened_urls.append(url)
            return open_result

    class _FakeNSWorkspace:
        workspace = _FakeWorkspace()

        @classmethod
        def sharedWorkspace(cls):
            return cls.workspace

    class _FakeCommand:
        def addTargetWithHandler_(self, _):
            return None

    class _FakeCommandCenter:
        @classmethod
        def sharedCommandCenter(cls):
            return cls()

        def togglePlayPauseCommand(self):
            return _FakeCommand()

        def playCommand(self):
            return _FakeCommand()

        def pauseCommand(self):
            return _FakeCommand()

        def nextTrackCommand(self):
            return _FakeCommand()

        def previousTrackCommand(self):
            return _FakeCommand()

        def stopCommand(self):
            return _FakeCommand()

        def changePlaybackPositionCommand(self):
            return _FakeCommand()

        def changePlaybackRateCommand(self):
            return _FakeCommand()

        def changeRepeatModeCommand(self):
            return _FakeCommand()

        def changeShuffleModeCommand(self):
            return _FakeCommand()

    class _FakeNowPlayingInfoCenter:
        @classmethod
        def defaultCenter(cls):
            return cls()

        def nowPlayingInfo(self):
            return None

        def setNowPlayingInfo_(self, _):
            return None

        def setPlaybackState_(self, _):
            return None

    foundation.NSMutableDictionary = _FakeNSMutableDictionary
    foundation.NSURL = _FakeNSURL
    appkit.NSImage = _FakeNSImage
    appkit.NSWorkspace = _FakeNSWorkspace
    mediaplayer.MPRemoteCommandCenter = _FakeCommandCenter
    mediaplayer.MPNowPlayingInfoCenter = _FakeNowPlayingInfoCenter
    mediaplayer.MPMusicPlaybackStatePlaying = "playing"
    mediaplayer.MPMusicPlaybackStatePaused = "paused"
    mediaplayer.MPMusicPlaybackStateStopped = "stopped"
    mediaplayer.MPMediaItemPropertyTitle = "title"
    mediaplayer.MPMediaItemPropertyArtist = "artist"
    mediaplayer.MPMediaItemPropertyAlbumTitle = "album"
    mediaplayer.MPMediaItemPropertyPlaybackDuration = "duration"
    mediaplayer.MPNowPlayingInfoPropertyPlaybackRate = "rate"
    mediaplayer.MPNowPlayingInfoPropertyElapsedPlaybackTime = "elapsed"
    mediaplayer.MPRemoteCommandHandlerStatusSuccess = 0
    mediaplayer.MPNowPlayingInfoPropertyDefaultPlaybackRate = "default_rate"
    mediaplayer.MPMediaItemPropertyAlbumArtist = "album_artist"
    mediaplayer.MPMediaItemPropertyComposer = "composer"
    mediaplayer.MPMediaItemPropertyGenre = "genre"
    mediaplayer.MPMediaItemPropertyArtwork = "artwork"

    monkeypatch.setitem(sys.modules, "Foundation", foundation)
    monkeypatch.setitem(sys.modules, "AppKit", appkit)
    monkeypatch.setitem(sys.modules, "MediaPlayer", mediaplayer)
    sys.modules.pop("aionowplaying.interface.macos", None)

    macos = importlib.import_module("aionowplaying.interface.macos")
    return macos, _FakeNSURL, _FakeNSWorkspace.workspace


def _install_fake_winrt(monkeypatch):
    winrt = ModuleType("winrt")
    system = ModuleType("winrt.system")
    windows = ModuleType("winrt.windows")
    foundation = ModuleType("winrt.windows.foundation")
    media = ModuleType("winrt.windows.media")
    playback = ModuleType("winrt.windows.media.playback")
    storage = ModuleType("winrt.windows.storage")
    streams = ModuleType("winrt.windows.storage.streams")

    class _FakeArray(list):
        pass

    class _FakeUri:
        def __init__(self, value):
            self.value = value

    class _FakeTimeline:
        def __init__(self):
            self.start_time = None
            self.min_seek_time = None
            self.max_seek_time = None
            self.end_time = None
            self.position = None

    class _FakeDisplayUpdater:
        def __init__(self):
            self.type = None
            self.app_media_id = None
            self.music_properties = ModuleType("music_properties")
            self.thumbnail = None

        def update(self):
            return None

    class _FakeControls:
        def __init__(self):
            self.display_updater = _FakeDisplayUpdater()
            self.sound_level = None
            self.playback_status = None
            self.playback_rate = None
            self.shuffle_enabled = None
            self.auto_repeat_mode = None
            self.is_stop_enabled = None
            self.is_play_enabled = None
            self.is_pause_enabled = None
            self.is_next_enabled = None
            self.is_previous_enabled = None

        def add_auto_repeat_mode_change_requested(self, _):
            return None

        def add_button_pressed(self, _):
            return None

        def add_playback_position_change_requested(self, _):
            return None

        def add_playback_rate_change_requested(self, _):
            return None

        def add_property_changed(self, _):
            return None

        def add_shuffle_enabled_change_requested(self, _):
            return None

        def update_timeline_properties(self, _):
            return None

    class _FakeCommandManager:
        is_enabled = False

    class _FakeMediaPlayer:
        def __init__(self):
            self.command_manager = _FakeCommandManager()
            self.system_media_transport_controls = _FakeControls()

    class _FakeRandomAccessStreamReference:
        @classmethod
        def create_from_uri(cls, _):
            return cls()

    class _FakeEnumValue:
        def __init__(self, value):
            self.value = value

    class _FakeEnumNamespace:
        MUSIC = _FakeEnumValue("music")
        IMAGE = _FakeEnumValue("image")
        VIDEO = _FakeEnumValue("video")
        PLAYING = _FakeEnumValue("playing")
        PAUSED = _FakeEnumValue("paused")
        STOPPED = _FakeEnumValue("stopped")
        NONE = _FakeEnumValue("none")
        LIST = _FakeEnumValue("list")
        TRACK = _FakeEnumValue("track")
        SOUND_LEVEL = _FakeEnumValue("sound_level")
        PLAY = _FakeEnumValue("play")
        PAUSE = _FakeEnumValue("pause")
        NEXT = _FakeEnumValue("next")
        PREVIOUS = _FakeEnumValue("previous")
        STOP = _FakeEnumValue("stop")

    system.Array = _FakeArray
    foundation.Uri = _FakeUri
    media.SystemMediaTransportControlsTimelineProperties = _FakeTimeline
    media.SystemMediaTransportControls = _FakeControls
    media.SystemMediaTransportControlsDisplayUpdater = _FakeDisplayUpdater
    media.MediaPlaybackStatus = _FakeEnumNamespace
    media.MediaPlaybackType = _FakeEnumNamespace
    media.MediaPlaybackAutoRepeatMode = _FakeEnumNamespace
    media.AutoRepeatModeChangeRequestedEventArgs = object
    media.SystemMediaTransportControlsButtonPressedEventArgs = object
    media.SystemMediaTransportControlsButton = _FakeEnumNamespace
    media.PlaybackPositionChangeRequestedEventArgs = object
    media.PlaybackRateChangeRequestedEventArgs = object
    media.SystemMediaTransportControlsPropertyChangedEventArgs = object
    media.SystemMediaTransportControlsProperty = _FakeEnumNamespace
    media.ShuffleEnabledChangeRequestedEventArgs = object
    playback.MediaPlayer = _FakeMediaPlayer
    streams.RandomAccessStreamReference = _FakeRandomAccessStreamReference

    monkeypatch.setitem(sys.modules, "winrt", winrt)
    monkeypatch.setitem(sys.modules, "winrt.system", system)
    monkeypatch.setitem(sys.modules, "winrt.windows", windows)
    monkeypatch.setitem(sys.modules, "winrt.windows.foundation", foundation)
    monkeypatch.setitem(sys.modules, "winrt.windows.media", media)
    monkeypatch.setitem(sys.modules, "winrt.windows.media.playback", playback)
    monkeypatch.setitem(sys.modules, "winrt.windows.storage", storage)
    monkeypatch.setitem(sys.modules, "winrt.windows.storage.streams", streams)
    sys.modules.pop("aionowplaying.interface.windows", None)

    return importlib.import_module("aionowplaying.interface.windows")


def test_on_open_uri_opens_valid_uri(monkeypatch):
    sentinel_url = object()
    macos, fake_nsurl, workspace = _install_fake_frameworks(
        monkeypatch,
        url_factory=lambda uri: sentinel_url if uri == "https://example.com" else None,
        open_result=True,
    )

    it = object.__new__(macos.MacOSInterface)
    asyncio.run(macos.MacOSInterface.on_open_uri(it, "https://example.com"))

    assert fake_nsurl.calls == ["https://example.com"]
    assert workspace.opened_urls == [sentinel_url]


def test_on_open_uri_rejects_invalid_uri(monkeypatch):
    macos, fake_nsurl, workspace = _install_fake_frameworks(
        monkeypatch,
        url_factory=lambda _uri: None,
        open_result=True,
    )

    it = object.__new__(macos.MacOSInterface)

    with pytest.raises(ValueError):
        asyncio.run(macos.MacOSInterface.on_open_uri(it, "not-a-uri"))

    assert fake_nsurl.calls == ["not-a-uri"]
    assert workspace.opened_urls == []


def test_on_open_uri_raises_when_workspace_open_fails(monkeypatch):
    sentinel_url = object()
    macos, fake_nsurl, workspace = _install_fake_frameworks(
        monkeypatch,
        url_factory=lambda uri: sentinel_url if uri == "https://example.com" else None,
        open_result=False,
    )

    it = object.__new__(macos.MacOSInterface)

    with pytest.raises(RuntimeError):
        asyncio.run(macos.MacOSInterface.on_open_uri(it, "https://example.com"))

    assert fake_nsurl.calls == ["https://example.com"]
    assert workspace.opened_urls == [sentinel_url]


def test_windows_open_uri_helper_opens_valid_uri(monkeypatch):
    windows = _install_fake_winrt(monkeypatch)
    calls = []
    monkeypatch.setattr(windows.webbrowser, "open", lambda uri: calls.append(uri) or True)

    result = windows._open_uri_with_system("https://example.com")

    assert result is None
    assert calls == ["https://example.com"]


def test_windows_open_uri_helper_rejects_empty_uri(monkeypatch):
    windows = _install_fake_winrt(monkeypatch)

    with pytest.raises(ValueError):
        windows._open_uri_with_system("")


def test_windows_open_uri_helper_raises_when_system_opener_fails(monkeypatch):
    windows = _install_fake_winrt(monkeypatch)
    monkeypatch.setattr(windows.webbrowser, "open", lambda uri: False)

    with pytest.raises(RuntimeError):
        windows._open_uri_with_system("https://example.com")
