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
        # Will be implemented in later tasks
        pass

    def _apply_metadata(self, metadata: dict[str, Any]) -> None:
        """Apply metadata to the playback properties."""
        # Will be implemented in later tasks
        pass