__all__ = ['select_interface', 'BaseInterface', 'PropertyName', 'LoopStatus', 'PlaybackPropertyName',
           'PlaybackProperties', 'PlaybackStatus', 'NowPlayingInterface']

from typing import Type

from src.aionowplaying.interface import select_interface, BaseInterface
from src.aionowplaying.interface.base import PropertyName, LoopStatus, PlaybackPropertyName, PlaybackProperties, \
    PlaybackStatus

NowPlayingInterface: Type[BaseInterface] = select_interface()
if NowPlayingInterface is None:
    raise NotImplemented()
