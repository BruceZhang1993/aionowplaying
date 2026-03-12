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