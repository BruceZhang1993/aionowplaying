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