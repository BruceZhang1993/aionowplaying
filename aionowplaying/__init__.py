from typing import Type

from aionowplaying.interface import select_interface, BaseInterface
from aionowplaying.interface.base import PropertyName, LoopStatus, PlaybackPropertyName, PlaybackProperties, \
    PlaybackStatus

NowPlayingInterface: Type[BaseInterface] = select_interface()
if NowPlayingInterface is None:
    raise NotImplemented()
