from typing import List, Optional

from aionowplaying.enum import PlaybackStatus
from aionowplaying.interface import MPInterface, MPPlayerInterface, MPTrackListInterface
from aionowplaying.model import Metadata


class ExampleMPInterface(MPInterface):
    @property
    def canQuit(self) -> bool:
        return True

    @property
    def canRaise(self) -> bool:
        return True

    @property
    def hasTrackList(self) -> bool:
        return True

    @property
    def id(self) -> str:
        return 'example_player'

    @property
    def identity(self) -> str:
        return 'Example Player'

    @property
    def supportedUriSchemes(self) -> List[str]:
        return ['file']

    @property
    def supportedMimeTypes(self) -> List[str]:
        return ['audio/mpeg']


class ExampleMPPlayerInterface(MPPlayerInterface):
    @property
    def canGoNext(self) -> bool:
        return True

    @property
    def canGoPrevious(self) -> bool:
        return True

    @property
    def canPause(self) -> bool:
        return True

    @property
    def canControl(self) -> bool:
        return True

    @property
    def canPlay(self) -> bool:
        return True

    @property
    def canSeek(self) -> bool:
        return True

    @property
    def playbackStatus(self) -> PlaybackStatus:
        return PlaybackStatus.Playing

    @property
    def metadata(self) -> Optional[Metadata]:
        metadata = Metadata(
            trackId='/ExamplePlayer/Track_01',
            length=100,
            artUrl='',
            album='Example Album'
        )
        return metadata

    @property
    def position(self) -> int:
        return 0
