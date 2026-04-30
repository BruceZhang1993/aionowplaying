__all__ = ['NowPlaying', 'select_interface', 'BaseInterface', 'PropertyName', 'LoopStatus',
           'PlaybackPropertyName', 'PlaybackProperties', 'PlaybackStatus', 'TrackListPropertyName']

import warnings
from typing import Type

from aionowplaying.nowplaying import NowPlaying
from aionowplaying.interface import select_interface, BaseInterface
from aionowplaying.interface.base import PropertyName, LoopStatus, PlaybackPropertyName, PlaybackProperties, \
    PlaybackStatus, TrackListPropertyName


def __getattr__(name: str):
    """Provide deprecated access to NowPlayingInterface."""
    if name == "NowPlayingInterface":
        warnings.warn(
            "NowPlayingInterface is deprecated. Use NowPlaying instead.",
            DeprecationWarning,
            stacklevel=2,
        )
        return select_interface()
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
