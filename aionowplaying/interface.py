from abc import ABCMeta, abstractmethod
from typing import List, Optional

from aionowplaying.enum import PlaybackStatus, LoopStatus
from aionowplaying.model import Metadata


# noinspection PyPep8Naming
class MPInterface(metaclass=ABCMeta):
    """
    Media player definitions of aionp
    All media players using aionp should implement this interface
    """

    @property
    @abstractmethod
    def canQuit(self) -> bool:
        """
        Returns whether if this media player can quit.
        You must implement `quit` method if canQuit is set to true.

        :return: true if this media player can quit
        :rtype: bool
        """
        pass

    @property
    def fullscreen(self) -> bool:
        """
        Returns whether if this media player is set fullscreen.
        You must implement this if canSetFullscreen is set to true.

        :rtype: bool
        :return: true if this media player is set fullscreen.
        """
        return False

    @fullscreen.setter
    def fullscreen(self, value: bool):
        """
        Your media player should be set to fullscreen if value is true, otherwise.
        You must implement this if canSetFullscreen is set to true.

        :type value: bool
        :param value: set this media player to fullscreen if true
        """
        pass

    @property
    def canSetFullscreen(self) -> bool:
        """
        Returns whether if this media player can set fullscreen.
        You must implement `fullscreen` getter&setter if canSetFullscreen is set to true.

        :return: true if this media player can set fullscreen.
        :rtype: bool
        """
        return False

    @property
    @abstractmethod
    def canRaise(self) -> bool:
        """
        Returns true if this media player can be bring to the front
        You must implement `raise_` if canRaise is set to true.

        :rtype: bool
        :return: true if this media player can be bring to the front
        """
        pass

    @property
    @abstractmethod
    def hasTrackList(self) -> bool:
        """
        Returns true if this media player has current playing list.
        You must support TrackListInterface if this property is set to true.

        :rtype: bool
        :return: true if this media player has current playing list.
        """
        pass

    @property
    @abstractmethod
    def identity(self) -> str:
        """A friendly name to identify the media player to users"""
        pass

    @property
    def desktopEntry(self) -> Optional[str]:
        """The basename of an installed .desktop file which complies with the Desktop entry specification,
        with the ".desktop" extension stripped"""
        return None

    @property
    @abstractmethod
    def supportedUriSchemes(self) -> List[str]:
        """
        The URI schemes supported by the media player.
        Example values are file, http, ...

        :rtype: List[str]
        """
        pass

    @property
    @abstractmethod
    def supportedMimeTypes(self) -> List[str]:
        """
        The mime-types supported by the media player.

        :rtype: List[str]
        """
        pass

    def raise_(self):
        """
        Brings the media player's user interface to the front
        You must implement if canRaise is set to true.
        """
        pass

    def quit(self):
        """
        Causes the media player to stop running
        You must implement this method if canQuit is set to true.
        """
        pass


# noinspection PyPep8Naming
class MPPlayerInterface(metaclass=ABCMeta):
    @property
    @abstractmethod
    def canGoNext(self) -> bool:
        pass

    def next(self):
        pass

    @property
    @abstractmethod
    def canGoPrevious(self) -> bool:
        pass

    def previous(self):
        pass

    @property
    @abstractmethod
    def canPause(self) -> bool:
        pass

    def pause(self):
        pass

    def playPause(self):
        pass

    @property
    @abstractmethod
    def canControl(self) -> bool:
        pass

    def stop(self):
        pass

    @property
    def loopStatus(self) -> Optional[LoopStatus]:
        return None

    @loopStatus.setter
    def loopStatus(self, status: LoopStatus):
        pass

    @property
    def shuffle(self) -> Optional[bool]:
        return None

    @shuffle.setter
    def shuffle(self, value: bool):
        pass

    @property
    def volume(self) -> Optional[float]:
        return None

    @volume.setter
    def volume(self, value: float):
        pass

    @property
    @abstractmethod
    def canPlay(self) -> bool:
        pass

    def play(self):
        pass

    @property
    @abstractmethod
    def canSeek(self) -> bool:
        pass

    def seek(self, offset: int):
        pass

    def setPosition(self, trackId: str, position: int):
        pass

    def openUri(self, uri: str):
        pass

    @property
    @abstractmethod
    def playbackStatus(self) -> PlaybackStatus:
        pass

    @property
    def rate(self) -> float:
        return 1.0

    @property
    def minimumRate(self) -> float:
        return 1.0

    @property
    def maximumRate(self) -> float:
        return 1.0

    @property
    @abstractmethod
    def metadata(self) -> Metadata:
        pass

    @property
    @abstractmethod
    def position(self) -> int:
        pass
