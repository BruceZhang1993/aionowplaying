import sys
from types import ModuleType, SimpleNamespace
from enum import Enum


def install_fake_winrt():
    if "winrt" in sys.modules:
        return

    winrt = ModuleType("winrt")
    winrt_system = ModuleType("winrt.system")
    winrt_windows = ModuleType("winrt.windows")
    winrt_foundation = ModuleType("winrt.windows.foundation")
    winrt_media = ModuleType("winrt.windows.media")
    winrt_media_playback = ModuleType("winrt.windows.media.playback")
    winrt_storage = ModuleType("winrt.windows.storage")
    winrt_streams = ModuleType("winrt.windows.storage.streams")

    class Array(list):
        pass

    winrt_system.Array = Array

    class Uri:
        def __init__(self, value):
            self.value = value

        def __repr__(self):
            return f"Uri({self.value!r})"

    winrt_foundation.Uri = Uri

    class MediaPlaybackStatus(Enum):
        PLAYING = 1
        PAUSED = 2
        STOPPED = 3

    class MediaPlaybackType(Enum):
        IMAGE = 1
        VIDEO = 2
        MUSIC = 3

    class MediaPlaybackAutoRepeatMode(Enum):
        NONE = 0
        LIST = 1
        TRACK = 2

    class SystemMediaTransportControlsButton(Enum):
        PLAY = 1
        PAUSE = 2
        NEXT = 3
        PREVIOUS = 4
        STOP = 5

    class SystemMediaTransportControlsProperty(Enum):
        SOUND_LEVEL = 1

    class SystemMediaTransportControlsTimelineProperties:
        def __init__(self):
            self.start_time = None
            self.end_time = None
            self.min_seek_time = None
            self.max_seek_time = None
            self.position = None

    class SystemMediaTransportControlsDisplayUpdater:
        def __init__(self):
            self.type = None
            self.app_media_id = None
            self.thumbnail = None
            self.update_called = False
            self.music_properties = SimpleNamespace(artist="", title="", album_title="")

        def update(self):
            self.update_called = True

    class SystemMediaTransportControls:
        def __init__(self):
            self.display_updater = SystemMediaTransportControlsDisplayUpdater()
            self.playback_status = None
            self.auto_repeat_mode = None
            self.is_stop_enabled = False
            self.is_play_enabled = False
            self.is_pause_enabled = False
            self.is_next_enabled = False
            self.is_previous_enabled = False
            self.shuffle_enabled = False
            self.playback_rate = 1.0
            self.sound_level = 0.5
            self._timeline = None
            self._handlers = {}

        def update_timeline_properties(self, timeline):
            self._timeline = timeline

        def add_auto_repeat_mode_change_requested(self, handler):
            self._handlers["auto_repeat"] = handler

        def add_button_pressed(self, handler):
            self._handlers["button_pressed"] = handler

        def add_playback_position_change_requested(self, handler):
            self._handlers["position"] = handler

        def add_playback_rate_change_requested(self, handler):
            self._handlers["rate"] = handler

        def add_property_changed(self, handler):
            self._handlers["property_changed"] = handler

        def add_shuffle_enabled_change_requested(self, handler):
            self._handlers["shuffle"] = handler

    class MediaPlayer:
        def __init__(self):
            self.system_media_transport_controls = SystemMediaTransportControls()

    class AutoRepeatModeChangeRequestedEventArgs:
        def __init__(self, requested_auto_repeat_mode):
            self.requested_auto_repeat_mode = requested_auto_repeat_mode

    class SystemMediaTransportControlsButtonPressedEventArgs:
        def __init__(self, button):
            self.button = button

    class PlaybackPositionChangeRequestedEventArgs:
        def __init__(self, requested_playback_position):
            self.requested_playback_position = requested_playback_position

    class PlaybackRateChangeRequestedEventArgs:
        def __init__(self, requested_playback_rate):
            self.requested_playback_rate = requested_playback_rate

    class SystemMediaTransportControlsPropertyChangedEventArgs:
        def __init__(self, property_):
            self.property = property_

    class ShuffleEnabledChangeRequestedEventArgs:
        def __init__(self, requested_shuffle_enabled):
            self.requested_shuffle_enabled = requested_shuffle_enabled

    winrt_media.SystemMediaTransportControlsTimelineProperties = SystemMediaTransportControlsTimelineProperties
    winrt_media.SystemMediaTransportControls = SystemMediaTransportControls
    winrt_media.SystemMediaTransportControlsDisplayUpdater = SystemMediaTransportControlsDisplayUpdater
    winrt_media.MediaPlaybackStatus = MediaPlaybackStatus
    winrt_media.MediaPlaybackType = MediaPlaybackType
    winrt_media.MediaPlaybackAutoRepeatMode = MediaPlaybackAutoRepeatMode
    winrt_media.AutoRepeatModeChangeRequestedEventArgs = AutoRepeatModeChangeRequestedEventArgs
    winrt_media.SystemMediaTransportControlsButtonPressedEventArgs = SystemMediaTransportControlsButtonPressedEventArgs
    winrt_media.SystemMediaTransportControlsButton = SystemMediaTransportControlsButton
    winrt_media.PlaybackPositionChangeRequestedEventArgs = PlaybackPositionChangeRequestedEventArgs
    winrt_media.PlaybackRateChangeRequestedEventArgs = PlaybackRateChangeRequestedEventArgs
    winrt_media.SystemMediaTransportControlsPropertyChangedEventArgs = SystemMediaTransportControlsPropertyChangedEventArgs
    winrt_media.SystemMediaTransportControlsProperty = SystemMediaTransportControlsProperty
    winrt_media.ShuffleEnabledChangeRequestedEventArgs = ShuffleEnabledChangeRequestedEventArgs

    winrt_media_playback.MediaPlayer = MediaPlayer

    class RandomAccessStreamReference:
        @staticmethod
        def create_from_uri(uri):
            return f"thumb:{uri.value}"

    winrt_streams.RandomAccessStreamReference = RandomAccessStreamReference

    sys.modules["winrt"] = winrt
    sys.modules["winrt.system"] = winrt_system
    sys.modules["winrt.windows"] = winrt_windows
    sys.modules["winrt.windows.foundation"] = winrt_foundation
    sys.modules["winrt.windows.media"] = winrt_media
    sys.modules["winrt.windows.media.playback"] = winrt_media_playback
    sys.modules["winrt.windows.storage"] = winrt_storage
    sys.modules["winrt.windows.storage.streams"] = winrt_streams


def install_fake_macos():
    if "Foundation" in sys.modules:
        return

    foundation = ModuleType("Foundation")
    media_player = ModuleType("MediaPlayer")

    class NSMutableDictionary(dict):
        @classmethod
        def dictionary(cls):
            return cls()

        def mutableCopy(self):
            return NSMutableDictionary(self)

    foundation.NSMutableDictionary = NSMutableDictionary

    class _Command:
        def __init__(self):
            self.handlers = []

        def addTargetWithHandler_(self, handler):
            self.handlers.append(handler)

    class MPRemoteCommandCenter:
        def __init__(self):
            self._toggle = _Command()
            self._play = _Command()
            self._pause = _Command()
            self._next = _Command()
            self._prev = _Command()

        @classmethod
        def sharedCommandCenter(cls):
            return cls()

        def togglePlayPauseCommand(self):
            return self._toggle

        def playCommand(self):
            return self._play

        def pauseCommand(self):
            return self._pause

        def nextTrackCommand(self):
            return self._next

        def previousTrackCommand(self):
            return self._prev

    class MPNowPlayingInfoCenter:
        def __init__(self):
            self._info = None
            self.playback_state = None

        @classmethod
        def defaultCenter(cls):
            return cls()

        def nowPlayingInfo(self):
            return self._info

        def setNowPlayingInfo_(self, info):
            self._info = info

        def setPlaybackState_(self, state):
            self.playback_state = state

    media_player.MPRemoteCommandCenter = MPRemoteCommandCenter
    media_player.MPNowPlayingInfoCenter = MPNowPlayingInfoCenter

    media_player.MPMediaItemPropertyTitle = "title"
    media_player.MPMediaItemPropertyArtist = "artist"
    media_player.MPMediaItemPropertyAlbumTitle = "album"
    media_player.MPMediaItemPropertyPlaybackDuration = "duration"
    media_player.MPNowPlayingInfoPropertyPlaybackRate = "playback_rate"
    media_player.MPNowPlayingInfoPropertyElapsedPlaybackTime = "elapsed"
    media_player.MPNowPlayingInfoPropertyDefaultPlaybackRate = "default_rate"

    media_player.MPMusicPlaybackStatePlaying = 1
    media_player.MPMusicPlaybackStatePaused = 2
    media_player.MPMusicPlaybackStateStopped = 3

    media_player.MPRemoteCommandHandlerStatusSuccess = 0

    sys.modules["Foundation"] = foundation
    sys.modules["MediaPlayer"] = media_player
