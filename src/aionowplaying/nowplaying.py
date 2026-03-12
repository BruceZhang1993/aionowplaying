from datetime import timedelta
from typing import Any, Callable

from aionowplaying.interface import _select_interface_impl
from aionowplaying.interface.base import (
    BaseInterface,
    LoopStatus,
    PlaybackProperties,
    PlaybackPropertyName,
    PlaybackStatus,
    PropertyName,
)


class NowPlaying:
    """
    Simplified interface for Now Playing integration.

    Example:
        player = NowPlaying("My Player")
        player.title = "Song Name"
        player.artist = ["Artist"]
        await player.start()
    """

    def __init__(
        self,
        name: str,
        identity: str | None = None,
        metadata: dict[str, Any] | None = None,
        on_play: Callable[[], Any] | None = None,
        on_pause: Callable[[], Any] | None = None,
        on_next: Callable[[], Any] | None = None,
        on_previous: Callable[[], Any] | None = None,
        on_seek: Callable[[timedelta], Any] | None = None,
        on_stop: Callable[[], Any] | None = None,
        on_volume: Callable[[float], Any] | None = None,
        on_shuffle: Callable[[bool], Any] | None = None,
        on_loop: Callable[[LoopStatus], Any] | None = None,
    ):
        self.name = name
        self._identity = identity or name
        self._interface: BaseInterface = _select_interface_impl()(name)
        self._interface.set_property(PropertyName.Identity, self._identity)

        # Store callbacks
        self._callbacks: dict[str, Callable] = {
            'on_play': on_play,
            'on_pause': on_pause,
            'on_next': on_next,
            'on_previous': on_previous,
            'on_seek': on_seek,
            'on_stop': on_stop,
            'on_volume': on_volume,
            'on_shuffle': on_shuffle,
            'on_loop': on_loop,
        }

        # Setup capabilities based on callbacks
        self._setup_capabilities()

        # Apply initial metadata
        if metadata:
            self._apply_metadata(metadata)

    def _setup_capabilities(self) -> None:
        """Setup playback capabilities based on provided callbacks."""
        control_callbacks = [
            'on_play', 'on_pause', 'on_next', 'on_previous',
            'on_seek', 'on_stop', 'on_volume', 'on_shuffle', 'on_loop'
        ]

        # Set CanControl if any control callback is registered
        has_control = any(self._callbacks.get(cb) for cb in control_callbacks)
        if has_control:
            self._interface.set_playback_property(PlaybackPropertyName.CanControl, True)

        # Set specific capabilities
        callback_capability_map = {
            'on_play': PlaybackPropertyName.CanPlay,
            'on_pause': PlaybackPropertyName.CanPause,
            'on_next': PlaybackPropertyName.CanGoNext,
            'on_previous': PlaybackPropertyName.CanGoPrevious,
            'on_seek': PlaybackPropertyName.CanSeek,
        }

        for callback_name, capability in callback_capability_map.items():
            if self._callbacks.get(callback_name):
                self._interface.set_playback_property(capability, True)

    def _apply_metadata(self, metadata: dict[str, Any]) -> None:
        """Apply metadata to the playback properties."""
        # Will be implemented in later tasks
        pass

    @staticmethod
    def _timedelta_to_microseconds(td: timedelta) -> int:
        """Convert timedelta to microseconds."""
        return int(td.total_seconds() * 1_000_000)

    @staticmethod
    def _microseconds_to_timedelta(us: int) -> timedelta:
        """Convert microseconds to timedelta."""
        return timedelta(microseconds=us)

    # Metadata properties

    @property
    def title(self) -> str:
        return self._interface._playback_properties.Metadata.title

    @title.setter
    def title(self, value: str):
        self._interface._playback_properties.Metadata.title = value

    @property
    def artist(self) -> list[str]:
        return self._interface._playback_properties.Metadata.artist

    @artist.setter
    def artist(self, value: list[str] | str):
        if isinstance(value, str):
            value = [value]
        self._interface._playback_properties.Metadata.artist = value

    @property
    def album(self) -> str:
        return self._interface._playback_properties.Metadata.album

    @album.setter
    def album(self, value: str):
        self._interface._playback_properties.Metadata.album = value

    @property
    def album_artist(self) -> list[str]:
        return self._interface._playback_properties.Metadata.albumArtist

    @album_artist.setter
    def album_artist(self, value: list[str] | str):
        if isinstance(value, str):
            value = [value]
        self._interface._playback_properties.Metadata.albumArtist = value

    @property
    def cover(self) -> str:
        return self._interface._playback_properties.Metadata.cover

    @cover.setter
    def cover(self, value: str):
        self._interface._playback_properties.Metadata.cover = value

    @property
    def url(self) -> str:
        return self._interface._playback_properties.Metadata.url

    @url.setter
    def url(self, value: str):
        self._interface._playback_properties.Metadata.url = value

    @property
    def track_number(self) -> int:
        return self._interface._playback_properties.Metadata.trackNumber

    @track_number.setter
    def track_number(self, value: int):
        self._interface._playback_properties.Metadata.trackNumber = value

    @property
    def duration(self) -> timedelta | None:
        us = self._interface._playback_properties.Metadata.duration
        if us == 0:
            return None
        return self._microseconds_to_timedelta(us)

    @duration.setter
    def duration(self, value: timedelta):
        self._interface._playback_properties.Metadata.duration = self._timedelta_to_microseconds(value)

    # Playback state properties

    @property
    def position(self) -> timedelta | None:
        """Get current playback position as timedelta."""
        us = self._interface.get_playback_property(PlaybackPropertyName.Position)
        if us == 0:
            return None
        return self._microseconds_to_timedelta(us)

    @position.setter
    def position(self, value: timedelta):
        """Set playback position from timedelta."""
        self._interface.set_playback_property(
            PlaybackPropertyName.Position,
            self._timedelta_to_microseconds(value)
        )

    @property
    def is_playing(self) -> bool:
        """Read-only property. Use set_playing() to change state."""
        return self._interface.get_playback_property(PlaybackPropertyName.PlaybackStatus) == PlaybackStatus.Playing

    @property
    def is_paused(self) -> bool:
        """Read-only property. Use set_paused() to change state."""
        return self._interface.get_playback_property(PlaybackPropertyName.PlaybackStatus) == PlaybackStatus.Paused

    @property
    def is_stopped(self) -> bool:
        """Read-only property. Use set_stopped() to change state."""
        return self._interface.get_playback_property(PlaybackPropertyName.PlaybackStatus) == PlaybackStatus.Stopped

    @property
    def volume(self) -> float:
        """Get playback volume (0.0 to 1.0)."""
        return self._interface.get_playback_property(PlaybackPropertyName.Volume)

    @volume.setter
    def volume(self, value: float):
        """Set playback volume (0.0 to 1.0)."""
        self._interface.set_playback_property(PlaybackPropertyName.Volume, value)

    @property
    def shuffle(self) -> bool:
        """Get shuffle state."""
        return self._interface.get_playback_property(PlaybackPropertyName.Shuffle)

    @shuffle.setter
    def shuffle(self, value: bool):
        """Set shuffle state."""
        self._interface.set_playback_property(PlaybackPropertyName.Shuffle, value)

    @property
    def loop_status(self) -> LoopStatus:
        """Get loop status (None, Track, or Playlist)."""
        return self._interface.get_playback_property(PlaybackPropertyName.LoopStatus)

    @loop_status.setter
    def loop_status(self, value: LoopStatus):
        """Set loop status."""
        self._interface.set_playback_property(PlaybackPropertyName.LoopStatus, value)

    @property
    def rate(self) -> float:
        """Get playback rate."""
        return self._interface.get_playback_property(PlaybackPropertyName.Rate)

    @rate.setter
    def rate(self, value: float):
        """Set playback rate."""
        self._interface.set_playback_property(PlaybackPropertyName.Rate, value)

    # State convenience methods

    def set_playing(self) -> None:
        """Set playback status to Playing."""
        self._interface.set_playback_property(PlaybackPropertyName.PlaybackStatus, PlaybackStatus.Playing)

    def set_paused(self) -> None:
        """Set playback status to Paused."""
        self._interface.set_playback_property(PlaybackPropertyName.PlaybackStatus, PlaybackStatus.Paused)

    def set_stopped(self) -> None:
        """Set playback status to Stopped."""
        self._interface.set_playback_property(PlaybackPropertyName.PlaybackStatus, PlaybackStatus.Stopped)