from enum import Enum
from typing import Any, List

from pydantic import BaseModel


class PropertyName(str, Enum):
    CanQuit = "CanQuit"
    CanSetFullscreen = "CanSetFullscreen"
    CanRaise = "CanRaise"
    HasTrackList = "HasTrackList"
    Identity = "Identity"
    DesktopEntry = "DesktopEntry"
    SupportedUriSchemes = "SupportedUriSchemes"
    SupportedMimeTypes = "SupportedMimeTypes"


class PlaybackPropertyName(str, Enum):
    PlaybackStatus = "PlaybackStatus"
    LoopStatus = "LoopStatus"
    Rate = "Rate"
    Shuffle = "Shuffle"
    Metadata = "Metadata"
    Volume = "Volume"
    Position = "Position"
    MinimumRate = "MinimumRate"
    MaximumRate = "MaximumRate"
    CanGoNext = "CanGoNext"
    CanGoPrevious = "CanGoPrevious"
    CanPlay = "CanPlay"
    CanPause = "CanPause"
    CanSeek = "CanSeek"
    CanControl = "CanControl"


class PlaybackStatus(str, Enum):
    Playing = "Playing"
    Paused = "Paused"
    Stopped = "Stopped"


class LoopStatus(str, Enum):
    None_ = "None"
    Track = "Track"
    Playlist = "Playlist"


class PlayerProperties(BaseModel):
    CanQuit: bool = False
    CanSetFullscreen: bool = False
    CanRaise: bool = False
    HasTrackList: bool = False
    Identity: str = ""
    DesktopEntry: str = ""
    SupportedUriSchemes: List[str] = []
    SupportedMimeTypes: List[str] = []


class PlaybackProperties(BaseModel):
    class MetadataBean(BaseModel):
        id_: str = ''
        duration: int = 0  # in microseconds
        cover: str = ''
        album: str = ''
        albumArtist: List[str] = []
        artist: List[str] = []
        lyrics: str = ''
        comments: List[str] = []
        composer: List[str] = []
        genre: List[str] = []
        lyricist: List[str] = []
        title: str = "Unknown"
        trackNumber: int = 0
        url: str = ''

    PlaybackStatus: 'PlaybackStatus' = PlaybackStatus.Stopped
    LoopStatus: 'LoopStatus' = LoopStatus.None_
    Rate: float = 1.0
    Shuffle: bool = False
    Metadata: MetadataBean = MetadataBean()
    Volume: float = 1.0
    Position: int = 0  # in microseconds
    MinimumRate: float = 1.0
    MaximumRate: float = 1.0
    CanGoNext: bool = False
    CanGoPrevious: bool = False
    CanPlay: bool = False
    CanPause: bool = False
    CanSeek: bool = False
    CanControl: bool = False


class BaseInterface:
    def __init__(self, name: str):
        pass

    def start(self):
        raise NotImplementedError()

    async def on_raise(self):
        raise NotImplementedError()

    async def on_quit(self):
        raise NotImplementedError()

    async def on_loop_status(self, status: LoopStatus):
        raise NotImplementedError()

    async def on_rate(self, rate: float):
        raise NotImplementedError()

    async def on_shuffle(self, shuffle: bool):
        raise NotImplementedError()

    async def on_volume(self, volume: float):
        raise NotImplementedError()

    async def on_next(self):
        raise NotImplementedError()

    async def on_previous(self):
        raise NotImplementedError()

    async def on_pause(self):
        raise NotImplementedError()

    async def on_play_pause(self):
        raise NotImplementedError()

    async def on_play(self):
        raise NotImplementedError()

    async def on_stop(self):
        raise NotImplementedError()

    async def on_seek(self, offset: int):
        raise NotImplementedError()

    def set_property(self, name: PropertyName, value: Any):
        raise NotImplementedError()

    def set_playback_property(self, name: PlaybackPropertyName, value: Any):
        raise NotImplementedError()
